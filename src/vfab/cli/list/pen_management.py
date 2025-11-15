"""
Pen configuration management commands.
"""

from __future__ import annotations

import typer
from ...codes import ExitCode
from ...utils import error_handler
from ...progress import show_status

try:
    from rich.console import Console
    from rich.prompt import Confirm
    from rich.table import Table

    console = Console()
except ImportError:
    console = None
    Confirm = None
    Table = None


def pen_list() -> None:
    """List available pen configurations."""
    try:
        from ...db import get_session
        from ...models import Pen

        with get_session() as session:
            pens = session.query(Pen).order_by(Pen.name).all()

            if not pens:
                if console:
                    console.print(
                        "No pens configured. Use 'vfab config pen-add' to add one."
                    )
                else:
                    print("No pens configured. Use 'vfab config pen-add' to add one.")
                return

            if console:
                console.print("🖊️  Available Pen Configurations")
                console.print("=" * 40)

                table = Table()
                table.add_column("ID", style="cyan", justify="right")
                table.add_column("Name", style="white")
                table.add_column("Width", style="white", justify="right")
                table.add_column("Speed", style="white", justify="right")
                table.add_column("Pressure", style="white", justify="right")
                table.add_column("Passes", style="white", justify="right")
                table.add_column("Color", style="white")

                for pen in pens:
                    color_display = getattr(pen, "color_hex", None) or "#000000"
                    width_mm = getattr(pen, "width_mm", None)
                    speed_cap = getattr(pen, "speed_cap", None)
                    pressure = getattr(pen, "pressure", None)
                    passes = getattr(pen, "passes", None)

                    table.add_row(
                        str(getattr(pen, "id", 0)),
                        getattr(pen, "name", "Unknown"),
                        f"{width_mm:.2f}mm" if width_mm else "N/A",
                        f"{speed_cap:.0f}" if speed_cap else "N/A",
                        str(pressure) if pressure else "N/A",
                        str(passes) if passes else "N/A",
                        color_display,
                    )

                console.print(table)
            else:
                print("Available Pen Configurations:")
                print("=" * 40)
                print(
                    f"{'ID':<4} {'Name':<20} {'Width':<8} {'Speed':<8} {'Pressure':<8} {'Passes':<8} {'Color'}"
                )
                print("-" * 40)

                for pen in pens:
                    color_display = getattr(pen, "color_hex", None) or "#000000"
                    width_mm = getattr(pen, "width_mm", 0) or 0
                    speed_cap = getattr(pen, "speed_cap", 0) or 0
                    pressure = getattr(pen, "pressure", 0) or 0
                    passes = getattr(pen, "passes", 0) or 0

                    print(
                        f"{getattr(pen, 'id', 0):<4} {getattr(pen, 'name', 'Unknown'):<20} {width_mm:>7.2f}mm {speed_cap:>7.0f} {pressure:>7} {passes:>7} {color_display}"
                    )

    except Exception as e:
        error_handler.handle(e)


def pen_add(
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
                if console:
                    console.print(f"❌ Pen '{name}' already exists", style="red")
                else:
                    print(f"Error: Pen '{name}' already exists")
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

            if console:
                console.print(f"✅ Added pen '{name}' successfully", style="green")
            else:
                print(f"Added pen '{name}' successfully")

    except typer.BadParameter:
        raise
    except Exception as e:
        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)


def pen_remove(name: str) -> None:
    """Remove a pen configuration."""
    try:
        from ...db import get_session
        from ...models import Pen

        with get_session() as session:
            # Find the pen
            pen = session.query(Pen).filter(Pen.name == name).first()
            if not pen:
                if console:
                    console.print(f"❌ Pen '{name}' not found", style="red")
                else:
                    print(f"Error: Pen '{name}' not found")
                raise typer.Exit(ExitCode.NOT_FOUND)

            # Check if pen is in use
            from ...models import Layer

            layers_using_pen = (
                session.query(Layer).filter(Layer.pen_id == pen.id).count()
            )
            if layers_using_pen > 0:
                if console:
                    console.print(
                        f"❌ Cannot remove pen '{name}': it is used by {layers_using_pen} layer(s)",
                        style="red",
                    )
                else:
                    print(
                        f"Error: Cannot remove pen '{name}': it is used by {layers_using_pen} layer(s)"
                    )
                raise typer.Exit(ExitCode.BUSY)

            # Confirm removal
            if console and Confirm:
                if not Confirm.ask(f"Remove pen '{name}'?"):
                    show_status("Operation cancelled", "info")
                    return
            else:
                response = input(f"Remove pen '{name}'? [y/N]: ").strip().lower()
                if response not in ["y", "yes"]:
                    print("Operation cancelled")
                    return

            # Remove the pen
            session.delete(pen)
            session.commit()

            if console:
                console.print(f"✅ Removed pen '{name}' successfully", style="green")
            else:
                print(f"Removed pen '{name}' successfully")

    except typer.Exit:
        raise
    except Exception as e:
        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)
