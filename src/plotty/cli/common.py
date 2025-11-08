"""
Common decorators and utilities for ploTTY CLI operations.

This module provides reusable patterns for CLI commands, particularly
for destructive operations that should use dry-run by default with --apply flag.
"""

from __future__ import annotations

from typing import Callable, Any, Optional
import typer

try:
    from rich.console import Console
    from rich.prompt import Confirm

    console = Console()
except ImportError:
    console = None
    Confirm = None


class DryRunContext:
    """Context manager for dry-run operations with consistent behavior."""

    def __init__(
        self,
        operation_name: str,
        apply_flag: bool,
        items: Optional[list] = None,
        item_type: str = "items",
        console_instance: Optional[Console] = None,
        operation_type: str = "destructive",  # destructive, state_change, file_op, physical
    ):
        self.operation_name = operation_name
        self.apply_flag = apply_flag
        self.items = items or []
        self.item_type = item_type
        self.console = console_instance or console
        self.confirmed = False
        self.operation_type = operation_type

    def show_preview(self) -> None:
        """Show what will be done in dry-run mode."""
        if not self.items:
            if self.console:
                self.console.print(
                    f"ℹ️  No {self.item_type} to {self.operation_name}", style="blue"
                )
            else:
                print(f"No {self.item_type} to {self.operation_name}")
            return

        # Customize message based on operation type
        if self.operation_type == "destructive":
            emoji = "🗑️"
            action = f"permanently {self.operation_name}"
        elif self.operation_type == "state_change":
            emoji = "🔄"
            action = f"{self.operation_name}"
        elif self.operation_type == "file_op":
            emoji = "📁"
            action = f"{self.operation_name}"
        elif self.operation_type == "physical":
            emoji = "⚙️"
            action = f"{self.operation_name}"
        else:
            emoji = "🔄"
            action = f"{self.operation_name}"

        if self.console:
            self.console.print(
                f"{emoji} Will {action} {len(self.items)} {self.item_type}:"
            )
            for item in self.items:
                self.console.print(f"  • {item}")

            # Customize call to action based on operation type
            if self.operation_type == "physical":
                self.console.print(
                    "💡 Use --apply to proceed with physical setup", style="yellow"
                )
            else:
                self.console.print("💡 Use --apply to actually execute", style="yellow")
        else:
            print(f"Will {action} {len(self.items)} {self.item_type}:")
            for item in self.items:
                print(f"  • {item}")
            print("Use --apply to actually execute")

    def confirm_execution(self) -> bool:
        """Ask for user confirmation before executing."""
        if not self.apply_flag:
            return False

        item_count = len(self.items)
        if item_count == 0:
            return False

        prompt = f"{self.operation_name.title()} {item_count} {self.item_type}?"
        if item_count == 1:
            prompt = f"{self.operation_name.title()} {self.items[0]}?"

        if self.console and Confirm:
            self.confirmed = Confirm.ask(prompt)
        else:
            response = input(f"{prompt} [y/N]: ").strip().lower()
            self.confirmed = response in ["y", "yes"]

        return self.confirmed

    def should_execute(self) -> bool:
        """Check if operation should be executed (apply flag + confirmation)."""
        if not self.apply_flag:
            self.show_preview()
            return False
        return self.confirm_execution()


def dry_run_apply(
    operation_name: str,
    item_type: str = "items",
    success_message: Optional[str] = None,
    error_message: Optional[str] = None,
) -> Callable:
    """
    Decorator for functions that should use dry-run by default with --apply flag.

    Args:
        operation_name: Name of the operation (e.g., "remove", "delete", "reset")
        item_type: Type of items being operated on (e.g., "jobs", "backups", "pens")
        success_message: Optional custom success message
        error_message: Optional custom error message

    Usage:
        @dry_run_apply("remove", "jobs")
        def remove_jobs(job_ids: list[str], apply: bool = False) -> None:
            # Function implementation
            # The decorator handles dry-run logic and confirmation
            pass
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            # Extract apply flag from kwargs
            apply_flag = kwargs.get("apply", False)

            # Call the original function to get items to operate on
            # The function should return a tuple of (items_to_process, execution_func)
            result = func(*args, **kwargs)

            # Handle different return patterns
            if isinstance(result, tuple) and len(result) == 2:
                items_to_process, execution_func = result
            elif callable(result):
                # If only execution function returned, assume no preview items
                items_to_process = []
                execution_func = result
            else:
                # If no execution function returned, just return the result
                return result

            # Create dry-run context
            ctx = DryRunContext(
                operation_name=operation_name,
                apply_flag=apply_flag,
                items=items_to_process,
                item_type=item_type,
            )

            # Check if should execute
            if not ctx.should_execute():
                return None

            # Execute the operation
            try:
                if items_to_process:
                    result = execution_func(items_to_process)
                else:
                    result = execution_func()

                # Show success message
                if success_message:
                    if console:
                        console.print(f"✅ {success_message}", style="green")
                    else:
                        print(f"✅ {success_message}")

                return result

            except Exception as e:
                if error_message:
                    if console:
                        console.print(f"❌ {error_message}: {e}", style="red")
                    else:
                        print(f"❌ {error_message}: {e}")
                raise

        return wrapper

    return decorator


def state_transition_apply(
    operation_name: str,
    success_message: Optional[str] = None,
    error_message: Optional[str] = None,
) -> Callable:
    """
    Decorator for state transition operations with dry-run/apply support.

    Usage:
        @state_transition_apply("start plotting", "Job started successfully")
        def start_command(job_id: str, apply: bool = False, dry_run: bool = False):
            # Function should return (job_id, current_state, target_state, execution_func)
            pass
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            # Extract flags
            apply_flag = kwargs.get("apply", False)
            dry_run_flag = kwargs.get("dry_run", False)
            preview_flag = kwargs.get("preview", False)

            # Call original function to get transition info
            result = func(*args, **kwargs)

            # Handle different return patterns
            if isinstance(result, tuple) and len(result) >= 3:
                job_id, current_state, target_state = result[:3]
                execution_func = result[3] if len(result) > 3 else None
            else:
                # If no transition info returned, just return result
                return result

            # Create state transition context
            ctx = StateTransitionContext(
                operation_name=operation_name,
                apply_flag=apply_flag,
                dry_run_flag=dry_run_flag,
                preview_flag=preview_flag,
                job_id=job_id or "",
                current_state=current_state or "",
                target_state=target_state or "",
            )

            # Check if should execute
            if not ctx.should_execute():
                return None

            # Execute state transition
            try:
                if execution_func:
                    result = execution_func()
                else:
                    result = None

                # Show success message
                if success_message:
                    if console:
                        console.print(f"✅ {success_message}", style="green")
                    else:
                        print(f"✅ {success_message}")

                return result

            except Exception as e:
                if error_message:
                    if console:
                        console.print(f"❌ {error_message}: {e}", style="red")
                    else:
                        print(f"❌ {error_message}: {e}")
                raise

        return wrapper

    return decorator


def physical_setup_apply(
    operation_name: str,
    success_message: Optional[str] = None,
    error_message: Optional[str] = None,
) -> Callable:
    """
    Decorator for physical setup operations with validation.

    Usage:
        @physical_setup_apply("plot job", "Physical setup validated, starting plot")
        def plot_command(job_id: str, apply: bool = False):
            # Function should return (requirements_dict, execution_func)
            pass
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            # Extract apply flag
            apply_flag = kwargs.get("apply", False)

            # Call original function to get requirements
            result = func(*args, **kwargs)

            # Handle different return patterns
            if isinstance(result, tuple) and len(result) == 2:
                requirements, execution_func = result
            elif callable(result):
                requirements = {}
                execution_func = result
            else:
                # If no execution function returned, just return result
                return result

            # Create physical setup context
            ctx = PhysicalSetupContext(
                operation_name=operation_name,
                apply_flag=apply_flag,
                requirements=requirements or {},
            )

            # Check if should execute
            if not ctx.should_execute():
                return None

            # Execute operation
            try:
                result = execution_func() if execution_func else None

                # Show success message
                if success_message:
                    if console:
                        console.print(f"✅ {success_message}", style="green")
                    else:
                        print(f"✅ {success_message}")

                return result

            except Exception as e:
                if error_message:
                    if console:
                        console.print(f"❌ {error_message}: {e}", style="red")
                    else:
                        print(f"❌ {error_message}: {e}")
                raise

        return wrapper

    return decorator


def enhanced_dry_run_apply(
    operation_name: str,
    item_type: str = "items",
    operation_type: str = "destructive",
    success_message: Optional[str] = None,
    error_message: Optional[str] = None,
) -> Callable:
    """
    Enhanced version of dry_run_apply with operation type support.

    Args:
        operation_name: Name of operation (e.g., "remove", "delete", "reset")
        item_type: Type of items being operated on (e.g., "jobs", "backups", "pens")
        operation_type: Type of operation ("destructive", "state_change", "file_op", "physical")
        success_message: Optional custom success message
        error_message: Optional custom error message
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            # Extract apply flag from kwargs
            apply_flag = kwargs.get("apply", False)

            # Call original function to get items to operate on
            result = func(*args, **kwargs)

            # Handle different return patterns
            if isinstance(result, tuple) and len(result) == 2:
                items_to_process, execution_func = result
            elif callable(result):
                # If only execution function returned, assume no preview items
                items_to_process = []
                execution_func = result
            else:
                # If no execution function returned, just return result
                return result

            # Create enhanced dry-run context
            ctx = DryRunContext(
                operation_name=operation_name,
                apply_flag=apply_flag,
                items=items_to_process,
                item_type=item_type,
                operation_type=operation_type,
            )

            # Check if should execute
            if not ctx.should_execute():
                return None

            # Execute operation
            try:
                if items_to_process:
                    result = execution_func(items_to_process)
                else:
                    result = execution_func()

                # Show success message
                if success_message:
                    if console:
                        console.print(f"✅ {success_message}", style="green")
                    else:
                        print(f"✅ {success_message}")

                return result

            except Exception as e:
                if error_message:
                    if console:
                        console.print(f"❌ {error_message}: {e}", style="red")
                    else:
                        print(f"❌ {error_message}: {e}")
                raise

        return wrapper

    return decorator

    return decorator


def confirm_destructive_operation(
    operation_name: str,
    item_description: str,
    apply_flag: bool,
    items: Optional[list] = None,
    console_instance: Optional[Console] = None,
) -> bool:
    """
    Standalone function for confirming destructive operations.

    This is useful for operations that don't fit the decorator pattern
    but still need consistent dry-run + apply behavior.

    Args:
        operation_name: Name of the operation (e.g., "remove", "delete")
        item_description: Description of what will be affected
        apply_flag: Whether --apply flag was provided
        items: Optional list of specific items to show in preview
        console_instance: Optional console instance

    Returns:
        True if operation should proceed, False otherwise
    """
    ctx = DryRunContext(
        operation_name=operation_name,
        apply_flag=apply_flag,
        items=items or [item_description],
        item_type="items",
        console_instance=console_instance,
    )

    return ctx.should_execute()


class StateTransitionContext:
    """Context for state transition operations (FSM-based)."""

    def __init__(
        self,
        operation_name: str,
        apply_flag: bool,
        dry_run_flag: bool = False,
        preview_flag: bool = False,
        job_id: Optional[str] = None,
        current_state: Optional[str] = None,
        target_state: Optional[str] = None,
        console_instance: Optional[Console] = None,
    ):
        self.operation_name = operation_name
        self.apply_flag = apply_flag
        self.dry_run_flag = dry_run_flag
        self.preview_flag = preview_flag
        self.job_id = job_id
        self.current_state = current_state
        self.target_state = target_state
        self.console = console_instance or console
        self.confirmed = False

        # Determine if we should execute
        self.should_execute_op = apply_flag and not dry_run_flag and not preview_flag

    def show_preview(self) -> None:
        """Show state transition preview."""
        if self.console:
            self.console.print(f"🔄 State Transition Preview: {self.operation_name}")
            if self.job_id:
                self.console.print(f"  Job ID: {self.job_id}")
            if self.current_state:
                self.console.print(f"  Current State: {self.current_state}")
            if self.target_state:
                self.console.print(f"  Target State: {self.target_state}")

            if self.should_execute_op:
                self.console.print("✅ Will execute state transition", style="green")
            else:
                self.console.print(
                    "💡 Use --apply to execute state transition", style="yellow"
                )
        else:
            print(f"State Transition Preview: {self.operation_name}")
            if self.job_id:
                print(f"  Job ID: {self.job_id}")
            if self.current_state:
                print(f"  Current State: {self.current_state}")
            if self.target_state:
                print(f"  Target State: {self.target_state}")

            if self.should_execute_op:
                print("Will execute state transition")
            else:
                print("Use --apply to execute state transition")

    def confirm_execution(self) -> bool:
        """Confirm state transition execution."""
        if not self.should_execute_op:
            return False

        if self.console:
            from rich.prompt import Confirm

            return Confirm.ask(f"Execute {self.operation_name} for job {self.job_id}?")
        else:
            response = (
                input(f"Execute {self.operation_name} for job {self.job_id}? [y/N]: ")
                .strip()
                .lower()
            )
            return response in ["y", "yes"]

    def should_execute(self) -> bool:
        """Check if operation should be executed."""
        self.show_preview()
        return self.confirm_execution()


class PhysicalSetupContext:
    """Context for physical setup validation operations."""

    def __init__(
        self,
        operation_name: str,
        apply_flag: bool,
        requirements: Optional[dict] = None,
        console_instance: Optional[Console] = None,
    ):
        self.operation_name = operation_name
        self.apply_flag = apply_flag
        self.requirements = requirements or {}
        self.console = console_instance or console
        self.confirmed = False

    def show_requirements(self) -> None:
        """Show physical setup requirements with enhanced guidance."""
        if self.console:
            self.console.print("📋 Physical Setup Checklist:", style="bold blue")

            # Show paper requirements with guidance
            if "paper_size" in self.requirements:
                paper_size = self.requirements["paper_size"]
                self.console.print(f"  📄 Paper: {paper_size}", style="cyan")
                self.console.print(
                    f"     • Load {paper_size} paper and align to plot area boundaries"
                )
                self.console.print("     • Ensure paper is flat and secured")

            # Show pen requirements with guidance
            if "pen_count" in self.requirements:
                pen_count = self.requirements["pen_count"]
                has_multipen = self.requirements.get("has_multipen", False)
                if has_multipen:
                    self.console.print(
                        f"  🖊️  Pens: {pen_count} (multipen setup)", style="cyan"
                    )
                    self.console.print(
                        f"     • Verify all {pen_count} pens are installed and functional"
                    )
                    self.console.print("     • Check pen mapping configuration")
                else:
                    self.console.print("  🖊️  Pen: Single pen setup", style="cyan")
                    self.console.print(
                        "     • Ensure pen is lowered and positioned correctly"
                    )
                    self.console.print("     • Test pen movement and ink flow")

            # Show any additional requirements
            for req_name, req_value in self.requirements.items():
                if req_name not in ["paper_size", "pen_count", "has_multipen"]:
                    self.console.print(f"  • {req_name}: {req_value}", style="cyan")
        else:
            print("Physical Setup Requirements:")
            for req_name, req_value in self.requirements.items():
                print(f"  • {req_name}: {req_value}")

    def confirm_physical_setup(self) -> bool:
        """Confirm physical setup is ready with enhanced prompts."""
        if not self.apply_flag:
            return False

        if self.console:
            from rich.prompt import Confirm

            # Show requirements first
            self.show_requirements()

            # Add visual separator
            self.console.print()
            self.console.print("🔍 Physical Setup Verification", style="bold yellow")
            self.console.print("Please verify the following before proceeding:")
            self.console.print("  • Paper is loaded and properly aligned")
            self.console.print("  • Pen(s) are installed and functional")
            self.console.print("  • AxiDraw is connected and powered on")
            self.console.print()

            # Ask for confirmation with clearer prompt
            return Confirm.ask(
                f"✅ Confirm physical setup is ready for {self.operation_name}?",
                default=False,
            )
        else:
            self.show_requirements()
            print("\nPhysical Setup Verification:")
            print("Please verify:")
            print("  • Paper is loaded and aligned")
            print("  • Pen(s) are installed and functional")
            print("  • Device is connected and powered")
            response = (
                input(
                    f"\nConfirm physical setup ready for {self.operation_name}? [y/N]: "
                )
                .strip()
                .lower()
            )
            return response in ["y", "yes"]

    def should_execute(self) -> bool:
        """Check if operation should proceed with enhanced guidance."""
        if not self.apply_flag:
            if self.console:
                self.console.print(
                    "💡 Physical setup check mode - use --apply to proceed with validation",
                    style="yellow",
                )
                self.console.print(
                    "   This will show setup requirements and request confirmation before plotting."
                )
            else:
                print(
                    "Physical setup check mode - use --apply to proceed with validation"
                )
                print(
                    "This will show setup requirements and request confirmation before plotting."
                )
            return False

        return self.confirm_physical_setup()


def create_apply_option(
    help_text: str = "Apply changes (dry-run by default)",
):
    """Create a standardized --apply option for CLI commands."""
    return typer.Option(False, "--apply", help=help_text)


def create_dry_run_option(
    help_text: str = "Preview changes without executing (dry-run mode)",
):
    """Create a standardized --dry-run option for CLI commands."""
    return typer.Option(False, "--dry-run", help=help_text)


def create_preview_option(
    help_text: str = "Preview operation without executing",
):
    """Create a standardized --preview option for CLI commands."""
    return typer.Option(False, "--preview", help=help_text)


def format_item_list(items: list, max_items: int = 10) -> str:
    """Format a list of items for display, truncating if too long."""
    if not items:
        return "none"

    if len(items) <= max_items:
        return ", ".join(str(item) for item in items)

    shown = items[:max_items]
    remaining = len(items) - max_items
    return f"{', '.join(str(item) for item in shown)} and {remaining} more..."
