"""
Paper configuration management commands.
"""

from __future__ import annotations

import typer

try:
    from rich.console import Console
    from rich.prompt import Confirm
    from rich.table import Table

    console = Console()
except ImportError:
    console = None
    Confirm = None
    Table = None


def paper_list(
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
    csv_output: bool = typer.Option(False, "--csv", help="Output in CSV format"),
) -> None:
    """List available paper configurations."""
    try:
        from ...db import get_session
        from ...models import Paper
        from ...utils import error_handler

        with get_session() as session:
            papers = session.query(Paper).order_by(Paper.name).all()

            if not papers:
                if json_output:
                    typer.echo("[]")
                elif csv_output:
                    typer.echo("ID,Name,Width,Height,Margin,Orientation")
                else:
                    typer.echo(
                        "No papers configured. Use 'plotty config paper-add' to add one."
                    )
                return

            # Prepare data
            headers = ["ID", "Name", "Width", "Height", "Margin", "Orientation"]
            rows = []

            for paper in papers:
                width = getattr(paper, "width_mm", 0)
                height = getattr(paper, "height_mm", 0)
                margin = getattr(paper, "margin_mm", 0)
                orientation = getattr(paper, "orientation", "Unknown")

                rows.append(
                    [
                        str(getattr(paper, "id", 0)),
                        getattr(paper, "name", "Unknown"),
                        f"{width:.1f}mm",
                        f"{height:.1f}mm",
                        f"{margin:.1f}mm",
                        orientation,
                    ]
                )

            # Output in requested format
            if json_output:
                import json

                papers_data = []
                for i, paper in enumerate(papers):
                    papers_data.append(
                        {
                            "id": getattr(paper, "id", 0),
                            "name": getattr(paper, "name", "Unknown"),
                            "width_mm": getattr(paper, "width_mm", 0),
                            "height_mm": getattr(paper, "height_mm", 0),
                            "margin_mm": getattr(paper, "margin_mm", 0),
                            "orientation": getattr(paper, "orientation", "Unknown"),
                        }
                    )
                typer.echo(json.dumps(papers_data, indent=2, default=str))
            elif csv_output:
                import csv
                import sys

                writer = csv.writer(sys.stdout)
                writer.writerow(headers)
                writer.writerows(rows)
            else:
                # Markdown output (default)
                typer.echo("# 📄 Available Paper Configurations")
                typer.echo()
                typer.echo("| " + " | ".join(headers) + " |")
                typer.echo("| " + " | ".join(["---"] * len(headers)) + " |")

                for row in rows:
                    typer.echo("| " + " | ".join(row) + " |")

    except Exception as e:
        from ...utils import error_handler

        error_handler.handle(e)


def paper_add(
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
                if console:
                    console.print(f"❌ Paper '{name}' already exists", style="red")
                else:
                    print(f"Error: Paper '{name}' already exists")
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

            if console:
                console.print(f"✅ Added paper '{name}' successfully", style="green")
            else:
                print(f"Added paper '{name}' successfully")

    except typer.BadParameter:
        raise
    except Exception as e:
        from ...utils import error_handler
        from ...codes import ExitCode

        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)


def paper_remove(name: str) -> None:
    """Remove a paper configuration."""
    try:
        from ...db import get_session
        from ...models import Paper
        from ...codes import ExitCode
        from ...progress import show_status

        with get_session() as session:
            # Find the paper
            paper = session.query(Paper).filter(Paper.name == name).first()
            if not paper:
                if console:
                    console.print(f"❌ Paper '{name}' not found", style="red")
                else:
                    print(f"Error: Paper '{name}' not found")
                raise typer.Exit(ExitCode.NOT_FOUND)

            # Check if paper is in use
            from ...models import Job

            jobs_using_paper = (
                session.query(Job).filter(Job.paper_id == paper.id).count()
            )
            if jobs_using_paper > 0:
                if console:
                    console.print(
                        f"❌ Cannot remove paper '{name}': it is used by {jobs_using_paper} job(s)",
                        style="red",
                    )
                else:
                    print(
                        f"Error: Cannot remove paper '{name}': it is used by {jobs_using_paper} job(s)"
                    )
                raise typer.Exit(ExitCode.BUSY)

            # Confirm removal
            if console and Confirm:
                if not Confirm.ask(f"Remove paper '{name}'?"):
                    show_status("Operation cancelled", "info")
                    return
            else:
                response = input(f"Remove paper '{name}'? [y/N]: ").strip().lower()
                if response not in ["y", "yes"]:
                    print("Operation cancelled")
                    return

            # Remove the paper
            session.delete(paper)
            session.commit()

            if console:
                console.print(f"✅ Removed paper '{name}' successfully", style="green")
            else:
                print(f"Removed paper '{name}' successfully")

    except typer.Exit:
        raise
    except Exception as e:
        from ...utils import error_handler
        from ...codes import ExitCode

        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)
