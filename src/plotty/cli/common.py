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
    ):
        self.operation_name = operation_name
        self.apply_flag = apply_flag
        self.items = items or []
        self.item_type = item_type
        self.console = console_instance or console
        self.confirmed = False

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

        if self.console:
            self.console.print(
                f"🔄 Will {self.operation_name} {len(self.items)} {self.item_type}:"
            )
            for item in self.items:
                self.console.print(f"  • {item}")
            self.console.print("💡 Use --apply to actually execute", style="yellow")
        else:
            print(f"Will {self.operation_name} {len(self.items)} {self.item_type}:")
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


def create_apply_option(
    help_text: str = "Apply changes (dry-run by default)",
):
    """Create a standardized --apply option for CLI commands."""
    return typer.Option(False, "--apply", help=help_text)


def format_item_list(items: list, max_items: int = 10) -> str:
    """Format a list of items for display, truncating if too long."""
    if not items:
        return "none"

    if len(items) <= max_items:
        return ", ".join(str(item) for item in items)

    shown = items[:max_items]
    remaining = len(items) - max_items
    return f"{', '.join(str(item) for item in shown)} and {remaining} more..."
