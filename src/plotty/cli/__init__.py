"""
CLI package for ploTTY.

This package contains the main CLI interface split into logical command groups.
"""

from __future__ import annotations

from importlib import metadata

import typer

from .add import add_app
from .check import check_app
from .info import info_app
from .interactive import interactive_command
from .commands import optimize_command, plan_command, queue_command, start_command
from .list import list_app
from .list.setup_wizard import setup
from .remove import remove_app
from .restart import restart_command
from .resume import resume_command
from .stats import stats_app
from .system import system_app

try:
    from .daemon import daemon_command
except ImportError:
    daemon_command = None
try:
    from .monitor import monitor_command
except ImportError:
    monitor_command = None

# Get version
try:
    __version__ = metadata.version("plotty")
except metadata.PackageNotFoundError:
    __version__ = "1.2.1"

# Create main app
app = typer.Typer(no_args_is_help=True)

# Add sub-apps and commands (alphabetical order)
app.add_typer(add_app, name="add", help="Add new files")
app.add_typer(check_app, name="check", help="System and device checking")
if daemon_command:
    app.command("daemon", help="Run ploTTY as a persistent daemon")(daemon_command)
app.add_typer(info_app, name="info", help="Information and monitoring commands")
app.command("interactive", help="Start an interactive plot")(interactive_command)
app.add_typer(list_app, name="list", help="List and manage resources")
if monitor_command:
    app.command("monitor", help="Real-time WebSocket monitoring")(monitor_command)
app.command("optimize", help="Optimize jobs for plotting")(optimize_command)
app.command("plan", help="Plan a job for plotting")(plan_command)
app.command("queue", help="Queue a job for plotting")(queue_command)
app.add_typer(remove_app, name="remove", help="Remove resources")
app.command("resume", help="Resume interrupted plotting jobs")(resume_command)
app.command("restart", help="Restart job from beginning")(restart_command)
app.add_typer(stats_app, name="stats", help="Statistics and analytics")
app.command("setup", help="Run setup wizard")(setup)
app.command("start", help="Start plotting a job")(start_command)
app.command("plot", help="Plot a job")(start_command)
app.add_typer(system_app, name="system", help="System management commands")


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", help="Show version and exit"),
):
    """ploTTY - Plotter management system."""
    if version:
        typer.echo(f"ploTTY v{__version__}")
        raise typer.Exit()

    # Initialize ploTTY on first run
    try:
        from ..init import is_first_run, initialize_plotty

        if is_first_run():
            try:
                from rich.console import Console

                console = Console()
                console.print(
                    "🎨 Welcome to ploTTY! Initializing configuration...",
                    style="bold blue",
                )
            except ImportError:
                print("🎨 Welcome to ploTTY! Initializing configuration...")

            if initialize_plotty():
                try:
                    from rich.console import Console

                    console = Console()
                    console.print(
                        "✅ Configuration initialized successfully!", style="green"
                    )
                    console.print(
                        "💡 Run 'plotty setup' for interactive configuration",
                        style="cyan",
                    )
                except ImportError:
                    print("✅ Configuration initialized successfully!")
                    print("💡 Run 'plotty setup' for interactive configuration")
            else:
                try:
                    from rich.console import Console

                    console = Console()
                    console.print(
                        "⚠️  Configuration initialization completed with warnings",
                        style="yellow",
                    )
                except ImportError:
                    print("⚠️  Configuration initialization completed with warnings")
    except Exception:
        # Don't let initialization break CLI functionality
        pass

    # Check for interrupted jobs before any command
    try:
        from ..config import load_config
        from ..recovery import detect_interrupted_jobs, prompt_interrupted_resume
        from pathlib import Path

        cfg = load_config(None)
        workspace = Path(cfg.workspace)

        # Get grace period from config or default to 5 minutes
        grace_minutes = 5  # Default value
        if hasattr(cfg, "recovery") and hasattr(
            cfg.recovery, "interrupt_grace_minutes"
        ):
            grace_minutes = cfg.recovery.interrupt_grace_minutes

        interrupted_jobs = detect_interrupted_jobs(workspace, grace_minutes)
        if interrupted_jobs:
            if prompt_interrupted_resume(interrupted_jobs):
                # User chose to resume - execute resume command
                from ..recovery import get_crash_recovery

                recovery = get_crash_recovery(workspace)
                resumed_count = 0

                for job_info in interrupted_jobs:
                    job_id = job_info["job_id"]
                    fsm = recovery.recover_job(job_id)
                    if fsm:
                        recovery.register_fsm(fsm)
                        resumed_count += 1

                if resumed_count > 0:
                    try:
                        from rich.console import Console

                        console = Console()
                        console.print(
                            f"✅ Resumed {resumed_count} interrupted jobs",
                            style="green",
                        )
                    except ImportError:
                        print(f"Resumed {resumed_count} interrupted jobs")

                    # Exit after resume to avoid running original command
                    raise typer.Exit(0)

    except Exception:
        # Don't let interrupt detection break CLI functionality
        pass

    # If no command and no version, show help
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


def main():
    """Main entry point for ploTTY CLI."""
    app()


if __name__ == "__main__":
    main()
