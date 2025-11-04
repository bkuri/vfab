"""
Add commands for ploTTY CLI.

This module provides commands for adding new resources like pens, paper, jobs, and tests.
"""

from __future__ import annotations

import typer
from pathlib import Path

# Create add command group
add_app = typer.Typer(no_args_is_help=True, help="Add new resources")


def add_job(
    src: str,
    name: str = typer.Option("", "--name", "-n", help="Job name"),
    paper: str = typer.Option("A3", "--paper", "-p", help="Paper size"),
) -> None:
    """Add a new job to workspace."""
    try:
        from ...config import load_config
        from ...utils import error_handler, validate_file_exists
        from ...progress import show_status
        import uuid
        import json

        cfg = load_config(None)

        # Validate source file exists
        src_path = Path(src)
        validate_file_exists(src_path, "Source SVG file")

        # Generate 6-character job ID for better usability
        job_id = uuid.uuid4().hex[:6]
        jdir = Path(cfg.workspace) / "jobs" / job_id

        # Create job directory
        jdir.mkdir(parents=True, exist_ok=True)

        # Copy source file
        (jdir / "src.svg").write_bytes(src_path.read_bytes())

        # Create job metadata
        job_data = {
            "id": job_id,
            "name": name or src_path.stem,
            "paper": paper,
            "state": "QUEUED",
            "config_status": "DEFAULTS",
            "created_at": str(Path.cwd()),
        }

        (jdir / "job.json").write_text(json.dumps(job_data, indent=2))

        show_status(f"✓ Added job {job_id}: {job_data['name']}", "success")
        print(job_id)

    except Exception as e:
        from ...utils import error_handler

        error_handler.handle(e)


def add_pen(
    name: str,
    width_mm: float,
    speed_cap: float,
    pressure: int,
    passes: int,
    color_hex: str = typer.Option(
        "#000000", "--color", "-c", help="Pen color in hex format"
    ),
) -> None:
    """Add a new pen configuration."""
    try:
        from ...db import get_session
        from ...models import Pen
        from ...codes import ExitCode

        # Validate color hex format
        if not color_hex.startswith("#"):
            color_hex = f"#{color_hex}"

        # Validate ranges
        if width_mm <= 0:
            raise typer.BadParameter("Width must be positive")
        if speed_cap <= 0:
            raise typer.BadParameter("Speed must be positive")
        if not (0 <= pressure <= 100):
            raise typer.BadParameter("Pressure must be between 0 and 100")
        if passes < 1:
            raise typer.BadParameter("Passes must be at least 1")

        with get_session() as session:
            # Check if pen already exists
            existing_pen = session.query(Pen).filter(Pen.name == name).first()
            if existing_pen:
                typer.echo(f"Error: Pen '{name}' already exists", err=True)
                raise typer.Exit(ExitCode.ALREADY_EXISTS)

            # Create new pen
            new_pen = Pen(
                name=name,
                width_mm=width_mm,
                speed_cap=speed_cap,
                pressure=pressure,
                passes=passes,
                color_hex=color_hex,
            )

            session.add(new_pen)
            session.commit()

            typer.echo(f"✅ Added pen '{name}' successfully")

    except typer.BadParameter:
        raise
    except Exception as e:
        from ...utils import error_handler
        from ...codes import ExitCode

        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)


def add_paper(
    name: str,
    width_mm: float,
    height_mm: float,
    margin_mm: float = typer.Option(10, "--margin", "-m", help="Margin in mm"),
    orientation: str = typer.Option(
        "portrait", "--orientation", "-o", help="Paper orientation"
    ),
) -> None:
    """Add a new paper configuration."""
    try:
        from ...db import get_session
        from ...models import Paper
        from ...codes import ExitCode

        # Validate inputs
        if width_mm <= 0:
            raise typer.BadParameter("Width must be positive")
        if height_mm <= 0:
            raise typer.BadParameter("Height must be positive")
        if margin_mm < 0:
            raise typer.BadParameter("Margin cannot be negative")
        if orientation not in ["portrait", "landscape"]:
            raise typer.BadParameter("Orientation must be 'portrait' or 'landscape'")

        with get_session() as session:
            # Check if paper already exists
            existing_paper = session.query(Paper).filter(Paper.name == name).first()
            if existing_paper:
                typer.echo(f"Error: Paper '{name}' already exists", err=True)
                raise typer.Exit(ExitCode.ALREADY_EXISTS)

            # Create new paper
            new_paper = Paper(
                name=name,
                width_mm=width_mm,
                height_mm=height_mm,
                margin_mm=margin_mm,
                orientation=orientation,
            )

            session.add(new_paper)
            session.commit()

            typer.echo(f"✅ Added paper '{name}' successfully")

    except typer.BadParameter:
        raise
    except Exception as e:
        from ...utils import error_handler
        from ...codes import ExitCode

        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)


# Register commands
add_app.command("job", help="Add a new job")(add_job)
add_app.command("pen", help="Add a new pen configuration")(add_pen)
add_app.command("paper", help="Add a new paper configuration")(add_paper)


def add_test(
    name: str,
    test_type: str = typer.Option(
        ..., "--type", "-t", help="Type of test (servo/camera/timing)"
    ),
    description: str = typer.Option("", "--description", "-d", help="Test description"),
) -> None:
    """Add a new device test."""
    try:
        from ...db import get_session
        from ...models import DeviceTest
        from ...codes import ExitCode

        # Validate test type
        valid_types = ["servo", "camera", "timing"]
        if test_type not in valid_types:
            raise typer.BadParameter(
                f"Test type must be one of: {', '.join(valid_types)}"
            )

        with get_session() as session:
            # Check if test already exists
            existing_test = (
                session.query(DeviceTest).filter(DeviceTest.name == name).first()
            )
            if existing_test:
                typer.echo(f"Error: Test '{name}' already exists", err=True)
                raise typer.Exit(ExitCode.ALREADY_EXISTS)

            # Create new test
            new_test = DeviceTest(
                name=name,
                test_type=test_type,
                description=description or f"{test_type.title()} test: {name}",
            )

            session.add(new_test)
            session.commit()

            typer.echo(f"✅ Added test '{name}' ({test_type}) successfully")

    except typer.BadParameter:
        raise
    except Exception as e:
        from ...utils import error_handler
        from ...codes import ExitCode

        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)


# Register test command
add_app.command("test", help="Add a new device test")(add_test)

__all__ = ["add_app"]
