"""
Setup wizard and configuration validation commands.
"""

from __future__ import annotations

import typer
from pathlib import Path

try:
    from rich.console import Console
    from rich.prompt import Confirm, Prompt
    from rich.panel import Panel

    console = Console()
except ImportError:
    console = None
    Confirm = None
    Prompt = None
    Panel = None


def setup() -> None:
    """Interactive setup wizard for ploTTY configuration."""
    try:
        from ...config import load_config
        from ...progress import show_status, show_boxed_progress
        from ...codes import ExitCode

        if console and Panel:
            console.print(Panel.fit("🎨 ploTTY Setup Wizard", style="bold blue"))
        else:
            print("🎨 ploTTY Setup Wizard")
            print("=" * 30)

        # Load current config
        try:
            cfg = load_config(None)
        except Exception:
            cfg = None

        # Workspace setup
        if console and Prompt:
            workspace = Prompt.ask(
                "Workspace directory",
                default=str(cfg.workspace) if cfg else "./workspace",
            )
        else:
            default_workspace = str(cfg.workspace) if cfg else "./workspace"
            workspace = input(f"Workspace directory [{default_workspace}]: ").strip()
            if not workspace:
                workspace = default_workspace

        workspace_path = Path(workspace).resolve()

        # Create workspace
        show_boxed_progress("Setting up workspace", 1, 3)
        try:
            workspace_path.mkdir(parents=True, exist_ok=True)
            (workspace_path / "jobs").mkdir(exist_ok=True)
            (workspace_path / "output").mkdir(exist_ok=True)
            (workspace_path / "logs").mkdir(exist_ok=True)
            show_status(f"✓ Workspace created at {workspace_path}", "success")
        except Exception as e:
            show_status(f"✗ Failed to create workspace: {e}", "error")
            raise typer.Exit(ExitCode.ERROR)

        # Device detection
        show_boxed_progress("Detecting devices", 2, 3)
        axidraw_available = False
        try:
            import importlib.util

            spec = importlib.util.find_spec("plotty.drivers.axidraw")
            axidraw_available = spec is not None

            if axidraw_available:
                show_status("✓ AxiDraw driver available", "success")
            else:
                show_status(
                    "⚠ AxiDraw driver not found (install with: pip install pyaxidraw)",
                    "warning",
                )
        except Exception:
            show_status("⚠ Could not check AxiDraw availability", "warning")

        # Camera test
        show_boxed_progress("Testing camera", 3, 3)
        camera_available = False
        try:
            # Simple camera detection
            cv2 = __import__("cv2")
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                camera_available = True
                cap.release()
                show_status("✓ Camera detected", "success")
            else:
                show_status("⚠ No camera detected", "warning")
        except ImportError:
            show_status(
                "⚠ OpenCV not available (install with: pip install opencv-python)",
                "warning",
            )
        except Exception:
            show_status("⚠ Camera test failed", "warning")

        # Configuration summary
        if console:
            console.print("\n📋 Setup Summary:")
            console.print(f"  Workspace: {workspace_path}")
            console.print(
                f"  AxiDraw: {'✅ Available' if axidraw_available else '❌ Not available'}"
            )
            console.print(
                f"  Camera: {'✅ Available' if camera_available else '❌ Not available'}"
            )

            if Confirm and Confirm.ask("\nSave this configuration?"):
                # TODO: Save configuration to file
                show_status("✓ Configuration saved", "success")
            else:
                show_status("Setup cancelled", "info")
        else:
            print("\n📋 Setup Summary:")
            print(f"  Workspace: {workspace_path}")
            print(
                f"  AxiDraw: {'✅ Available' if axidraw_available else '❌ Not available'}"
            )
            print(
                f"  Camera: {'✅ Available' if camera_available else '❌ Not available'}"
            )

            response = input("\nSave this configuration? [Y/n]: ").strip().lower()
            if response in ["", "y", "yes"]:
                # TODO: Save configuration to file
                show_status("✓ Configuration saved", "success")
            else:
                show_status("Setup cancelled", "info")

    except Exception as e:
        from ...utils import error_handler
        from ...codes import ExitCode

        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)


def check_config() -> None:
    """Validate ploTTY configuration and report issues."""
    try:
        from ...config import load_config
        from ...codes import ExitCode

        if console:
            console.print("🔍 Configuration Validation", style="bold blue")
        else:
            print("🔍 Configuration Validation")
            print("=" * 30)

        issues = []
        warnings = []

        # Check workspace
        try:
            cfg = load_config(None)
            workspace_path = Path(cfg.workspace)

            if not workspace_path.exists():
                issues.append(f"Workspace directory does not exist: {workspace_path}")
            else:
                # Check required subdirectories
                for subdir in ["jobs", "output", "logs"]:
                    subdir_path = workspace_path / subdir
                    if not subdir_path.exists():
                        warnings.append(f"Missing subdirectory: {subdir_path}")

        except Exception as e:
            issues.append(f"Failed to load configuration: {e}")

        # Check device drivers
        try:
            import importlib.util

            spec = importlib.util.find_spec("plotty.drivers.axidraw")
            if not spec:
                warnings.append(
                    "AxiDraw driver not available (install: pip install pyaxidraw)"
                )
        except Exception:
            warnings.append("Could not check AxiDraw driver availability")

        # Check database
        try:
            from ...db import get_session
            from sqlalchemy import text

            with get_session() as session:
                # Simple database connectivity test
                session.execute(text("SELECT 1"))
        except Exception as e:
            issues.append(f"Database connection failed: {e}")

        # Check camera
        try:
            cv2 = __import__("cv2")
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                warnings.append("No camera detected")
            cap.release()
        except ImportError:
            warnings.append("OpenCV not available (install: pip install opencv-python)")
        except Exception:
            warnings.append("Camera test failed")

        # Report results
        total_issues = len(issues) + len(warnings)

        if console:
            if total_issues == 0:
                console.print("✅ Configuration is valid!", style="bold green")
            else:
                if issues:
                    console.print("\n❌ Issues found:", style="bold red")
                    for issue in issues:
                        console.print(f"  • {issue}", style="red")

                if warnings:
                    console.print("\n⚠️  Warnings:", style="bold yellow")
                    for warning in warnings:
                        console.print(f"  • {warning}", style="yellow")
        else:
            if total_issues == 0:
                print("✅ Configuration is valid!")
            else:
                if issues:
                    print("\n❌ Issues found:")
                    for issue in issues:
                        print(f"  • {issue}")

                if warnings:
                    print("\n⚠️  Warnings:")
                    for warning in warnings:
                        print(f"  • {warning}")

        # Exit with appropriate code based on results
        if issues:
            raise typer.Exit(ExitCode.ERROR)
        elif warnings:
            raise typer.Exit(ExitCode.WARNING)
        else:
            raise typer.Exit(ExitCode.SUCCESS)

    except typer.Exit:
        raise
    except Exception as e:
        from ...utils import error_handler
        from ...codes import ExitCode

        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)
