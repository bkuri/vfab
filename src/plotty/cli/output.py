"""
Standardized output utilities for ploTTY CLI.

All CLI commands should use these utilities to ensure consistent
markdown formatting with Rich rendering by default.
"""

from __future__ import annotations

import json
import csv
import sys
from typing import Any, Dict, List, Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.text import Text

    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    console = None
    Table = None
    Panel = None
    Markdown = None
    Text = None
    RICH_AVAILABLE = False


class OutputFormatter:
    """Standardized output formatter for CLI commands."""

    def __init__(self, title: Optional[str] = None):
        self.title = title
        self.sections: List[Dict[str, Any]] = []

    def add_section(self, title: str, content: Any, section_type: str = "text") -> None:
        """Add a section to the output."""
        self.sections.append({"title": title, "content": content, "type": section_type})

    def add_table(
        self,
        title: str,
        headers: List[str],
        rows: List[List[str]],
        title_style: str = "bold",
    ) -> None:
        """Add a table section."""
        self.add_section(
            title,
            {"headers": headers, "rows": rows, "title_style": title_style},
            "table",
        )

    def add_key_value(self, title: str, data: Dict[str, str]) -> None:
        """Add a key-value section."""
        self.add_section(title, data, "key_value")

    def render(
        self,
        format_type: str = "rich",
        json_output: bool = False,
        csv_output: bool = False,
    ) -> None:
        """Render the output in the specified format."""
        if json_output:
            self._render_json()
        elif csv_output:
            self._render_csv()
        elif format_type == "rich" and RICH_AVAILABLE:
            self._render_rich()
        else:
            self._render_markdown()

    def _render_json(self) -> None:
        """Render as JSON."""
        output_data = {"title": self.title, "sections": self.sections}
        json.dump(output_data, sys.stdout, indent=2, default=str)
        sys.stdout.write("\n")

    def _render_csv(self) -> None:
        """Render as CSV (only table sections)."""
        writer = csv.writer(sys.stdout)

        for section in self.sections:
            if section["type"] == "table":
                table_data = section["content"]
                writer.writerow([section["title"]])
                writer.writerow(table_data["headers"])
                writer.writerows(table_data["rows"])
                writer.writerow([])  # Empty row between tables

    def _render_rich(self) -> None:
        """Render with Rich (default)."""
        if not console:
            self._render_markdown()
            return

        if self.title and Panel and Text:
            title_panel = Panel(
                Text(self.title, style="bold white"),
                border_style="blue",
                padding=(0, 1),
            )
            console.print(title_panel)
            console.print()

        for section in self.sections:
            if section["type"] == "text":
                console.print(f"## {section['title']}")
                console.print(section["content"])
                console.print()

            elif section["type"] == "table" and Table:
                table_data = section["content"]
                table = Table(title=section["title"])

                for header in table_data["headers"]:
                    table.add_column(header, style="cyan")

                for row in table_data["rows"]:
                    table.add_row(*row)

                console.print(table)
                console.print()

            elif section["type"] == "key_value" and Table:
                kv_table = Table(title=section["title"], show_header=False)
                kv_table.add_column("Property", style="cyan")
                kv_table.add_column("Value", style="white")

                for key, value in section["content"].items():
                    kv_table.add_row(key, value)

                console.print(kv_table)
                console.print()

    def _render_markdown(self) -> None:
        """Render as markdown."""
        if self.title:
            sys.stdout.write(f"# {self.title}\n\n")

        for section in self.sections:
            if section["type"] == "text":
                sys.stdout.write(f"## {section['title']}\n")
                sys.stdout.write(f"{section['content']}\n\n")

            elif section["type"] == "table":
                table_data = section["content"]
                sys.stdout.write(f"## {section['title']}\n")
                sys.stdout.write("| " + " | ".join(table_data["headers"]) + " |\n")
                sys.stdout.write(
                    "| " + " | ".join(["---"] * len(table_data["headers"])) + " |\n"
                )

                for row in table_data["rows"]:
                    sys.stdout.write(
                        "| " + " | ".join(str(cell) for cell in row) + " |\n"
                    )
                sys.stdout.write("\n")

            elif section["type"] == "key_value":
                sys.stdout.write(f"## {section['title']}\n")
                for key, value in section["content"].items():
                    sys.stdout.write(f"- **{key}**: {value}\n")
                sys.stdout.write("\n")


def render_simple_table(
    title: str,
    headers: List[str],
    rows: List[List[str]],
    json_output: bool = False,
    csv_output: bool = False,
) -> None:
    """Quick utility to render a simple table."""
    formatter = OutputFormatter(title)
    formatter.add_table(title, headers, rows)
    formatter.render("rich", json_output, csv_output)


def render_key_value(
    title: str,
    data: Dict[str, str],
    json_output: bool = False,
    csv_output: bool = False,
) -> None:
    """Quick utility to render key-value data."""
    formatter = OutputFormatter(title)
    formatter.add_key_value(title, data)
    formatter.render("rich", json_output, csv_output)


def render_markdown_content(content: str, json_output: bool = False) -> None:
    """Render markdown content directly."""
    if json_output:
        json.dump({"content": content}, sys.stdout, indent=2)
        sys.stdout.write("\n")
    elif RICH_AVAILABLE and Markdown and console:
        console.print(Markdown(content))
    else:
        sys.stdout.write(f"{content}\n")


def format_time(seconds: Optional[float]) -> str:
    """Format time in seconds to human readable format."""
    if seconds is None:
        return "Unknown"

    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def format_state(state: str) -> str:
    """Format job state with color."""
    if not RICH_AVAILABLE:
        return state

    state_colors = {
        "NEW": "blue",
        "QUEUED": "yellow",
        "ANALYZED": "cyan",
        "OPTIMIZED": "green",
        "READY": "bright_green",
        "ARMED": "magenta",
        "PLOTTING": "red",
        "PAUSED": "yellow",
        "COMPLETED": "green",
        "ABORTED": "red",
        "FAILED": "bright_red",
    }

    color = state_colors.get(state, "white")
    return f"[{color}]{state}[/{color}]"


def format_status(
    status: bool,
    true_text: str = "✅ Available",
    false_text: str = "❌ Not Available",
) -> str:
    """Format boolean status with emoji."""
    return true_text if status else false_text
