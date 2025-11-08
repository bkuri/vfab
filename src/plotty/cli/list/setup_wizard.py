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
        from ...config import load_config, Settings
        from ...progress import show_status, show_boxed_progress
        from ...codes import ExitCode

        if console and Panel:
            console.print(Panel.fit("🎨 ploTTY Setup Wizard", style="bold blue"))
        else:
            print("🎨 ploTTY Setup Wizard")
            print("=" * 30)

        # Load current config
        cfg = None
        try:
            cfg = load_config(None)
        except Exception:
            # Use default config if loading fails
            cfg = Settings()

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

        # Device detection using new DeviceDetector
        show_boxed_progress("Detecting devices", 2, 3)
        axidraw_available = False
        camera_available = False
        detector = None

        try:
            from ...detection import DeviceDetector

            # Use device config for remote detection if available
            remote_host = (
                getattr(cfg.device, "remote_detection_host", None) if cfg else None
            )
            timeout = getattr(cfg.device, "detection_timeout", 5) if cfg else 5

            detector = DeviceDetector(remote_host=remote_host, timeout=timeout)

            # Detect AxiDraw
            axidraw_result = detector.detect_axidraw_devices()
            axidraw_available = axidraw_result["count"] > 0

            if axidraw_available:
                accessible = (
                    "accessible" if axidraw_result["accessible"] else "connected"
                )
                show_status(
                    f"✓ AxiDraw {accessible} ({axidraw_result['count']} device{'s' if axidraw_result['count'] > 1 else ''})",
                    "success",
                )
            elif axidraw_result["installed"]:
                show_status("⚠ AxiDraw installed but no devices connected", "warning")
            else:
                show_status(
                    "⚠ AxiDraw not installed (install with: pip install pyaxidraw)",
                    "warning",
                )

        except Exception:
            show_status("⚠ Could not check AxiDraw availability", "warning")

        try:
            from ...detection import DeviceDetector

            # Detect Camera (reuse detector if available)
            if detector is not None:
                camera_result = detector.detect_camera_devices()
            else:
                # detector not defined, create new one
                remote_host = (
                    getattr(cfg.device, "remote_detection_host", None) if cfg else None
                )
                timeout = getattr(cfg.device, "detection_timeout", 5) if cfg else 5
                detector = DeviceDetector(remote_host=remote_host, timeout=timeout)
                camera_result = detector.detect_camera_devices()
            camera_available = camera_result["count"] > 0

            if camera_available:
                if camera_result["accessible"]:
                    show_status(
                        f"✓ Camera connected ({camera_result['count']} device{'s' if camera_result['count'] > 1 else ''})",
                        "success",
                    )
                elif camera_result["motion_running"]:
                    show_status(
                        "⚠ Camera connected but blocked (motion service running)",
                        "warning",
                    )
                else:
                    show_status("⚠ Camera connected but inaccessible", "warning")
            else:
                show_status("⚠ No camera devices found", "warning")

        except Exception:
            show_status("⚠ Camera detection failed", "warning")

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
                # Save configuration to file
                try:
                    from ...config import save_config, Settings

                    try:
                        from ...init import get_default_config_path
                    except ImportError:
                        # Fallback if init module not available
                        import platformdirs

                        def get_default_config_path() -> Path:
                            return (
                                Path(platformdirs.user_config_dir("plotty"))
                                / "config.yaml"
                            )

                    # Create updated configuration
                    if cfg is None:
                        cfg = Settings()

                    # Update workspace path
                    cfg.workspace = str(workspace_path)

                    # Save configuration to XDG config directory
                    config_path = get_default_config_path()
                    save_config(cfg, str(config_path))
                    show_status(f"✓ Configuration saved to {config_path}", "success")

                except Exception as e:
                    show_status(f"✗ Failed to save configuration: {e}", "error")
                    raise typer.Exit(ExitCode.ERROR)
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
                # Save configuration to file
                try:
                    from ...config import save_config, Settings

                    # Create updated configuration
                    if cfg is None:
                        cfg = Settings()

                    # Update workspace path
                    cfg.workspace = str(workspace_path)

                    # Save configuration
                    save_config(cfg)
                    show_status(
                        "✓ Configuration saved to config/config.yaml", "success"
                    )

                except Exception as e:
                    show_status(f"✗ Failed to save configuration: {e}", "error")
                    raise typer.Exit(ExitCode.ERROR)
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

        # Load configuration for validation
        cfg = None
        try:
            cfg = load_config(None)
        except Exception:
            from ...config import Settings

            cfg = Settings()

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

        # Check device drivers using DeviceDetector
        try:
            from ...detection import DeviceDetector

            remote_host = (
                getattr(cfg.device, "remote_detection_host", None) if cfg else None
            )
            timeout = getattr(cfg.device, "detection_timeout", 5) if cfg else 5

            detector = DeviceDetector(remote_host=remote_host, timeout=timeout)

            # Check AxiDraw
            axidraw_result = detector.detect_axidraw_devices()
            if axidraw_result["count"] == 0:
                if axidraw_result["installed"]:
                    warnings.append("AxiDraw installed but no devices connected")
                else:
                    warnings.append(
                        "AxiDraw not available (install: pip install pyaxidraw)"
                    )

            # Check Camera
            camera_result = detector.detect_camera_devices()
            if camera_result["count"] == 0:
                warnings.append("No camera devices found")
            elif not camera_result["accessible"] and camera_result["motion_running"]:
                warnings.append("Camera connected but blocked by motion service")

        except Exception:
            warnings.append("Could not check device availability")

        # Check database
        try:
            from ...db import get_session
            from sqlalchemy import text

            with get_session() as session:
                # Simple database connectivity test
                session.execute(text("SELECT 1"))
        except Exception as e:
            issues.append(f"Database connection failed: {e}")

        # Report results with actionable suggestions
        total_issues = len(issues) + len(warnings)

        if console:
            if total_issues == 0:
                console.print("✅ Configuration is valid!", style="bold green")
            else:
                if issues:
                    console.print("\n❌ Issues found:", style="bold red")
                    for issue in issues:
                        console.print(f"  • {issue}", style="red")
                        # Add actionable suggestions for common issues
                        if "Workspace directory does not exist" in issue:
                            console.print("    💡 Run: plotty setup", style="dim cyan")
                        elif "Failed to load configuration" in issue:
                            console.print(
                                "    💡 Check: config/config.yaml exists and is valid",
                                style="dim cyan",
                            )
                        elif "Database connection failed" in issue:
                            console.print(
                                "    💡 Run: uv run alembic upgrade head",
                                style="dim cyan",
                            )

                if warnings:
                    console.print("\n⚠️  Warnings:", style="bold yellow")
                    for warning in warnings:
                        console.print(f"  • {warning}", style="yellow")
                        # Add actionable suggestions for common warnings
                        if "Missing subdirectory" in warning:
                            subdir = warning.split(": ")[1]
                            console.print(
                                f"    💡 Run: mkdir -p {subdir}", style="dim cyan"
                            )
                        elif "AxiDraw installed but no devices connected" in warning:
                            console.print(
                                "    💡 Connect your AxiDraw device and check USB",
                                style="dim cyan",
                            )
                        elif "AxiDraw not available" in warning:
                            console.print(
                                "    💡 Run: uv pip install pyaxidraw", style="dim cyan"
                            )
                        elif "No camera devices found" in warning:
                            console.print(
                                "    💡 Connect a camera or check /dev/video* devices",
                                style="dim cyan",
                            )
                        elif (
                            "Camera connected but blocked by motion service" in warning
                        ):
                            console.print(
                                "    💡 Run: sudo systemctl stop motion",
                                style="dim cyan",
                            )
                        elif "Could not check device availability" in warning:
                            console.print(
                                "    💡 Check device permissions and USB connections",
                                style="dim cyan",
                            )
        else:
            if total_issues == 0:
                print("✅ Configuration is valid!")
            else:
                if issues:
                    print("\n❌ Issues found:")
                    for issue in issues:
                        print(f"  • {issue}")
                        # Add actionable suggestions for common issues
                        if "Workspace directory does not exist" in issue:
                            print("    💡 Run: plotty setup")
                        elif "Failed to load configuration" in issue:
                            print(
                                "    💡 Check: config/config.yaml exists and is valid"
                            )
                        elif "Database connection failed" in issue:
                            print("    💡 Run: uv run alembic upgrade head")

                if warnings:
                    print("\n⚠️  Warnings:")
                    for warning in warnings:
                        print(f"  • {warning}")
                        # Add actionable suggestions for common warnings
                        if "Missing subdirectory" in warning:
                            subdir = warning.split(": ")[1]
                            print(f"    💡 Run: mkdir -p {subdir}")
                        elif "AxiDraw installed but no devices connected" in warning:
                            print("    💡 Connect your AxiDraw device and check USB")
                        elif "AxiDraw not available" in warning:
                            print("    💡 Run: uv pip install pyaxidraw")
                        elif "No camera devices found" in warning:
                            print(
                                "    💡 Connect a camera or check /dev/video* devices"
                            )
                        elif (
                            "Camera connected but blocked by motion service" in warning
                        ):
                            print("    💡 Run: sudo systemctl stop motion")
                        elif "Could not check device availability" in warning:
                            print("    💡 Check device permissions and USB connections")

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
