"""
Output formatting utilities for ploTTY status commands.

This module provides shared functions for handling different output formats
(Rich markdown, plain markdown, JSON, CSV) with automatic redirection detection.
"""

from __future__ import annotations

import json
import sys
import csv
from typing import Any, Dict, List, Optional, Union

from rich.console import Console
from rich.markdown import Markdown


class OutputManager:
    """Manages output formatting and rendering for status commands."""

    def __init__(self):
        self._is_redirected = not sys.stdout.isatty()
        self._console = (
            Console(force_terminal=False, legacy_windows=False)
            if self._is_redirected
            else Console()
        )

    def is_redirected(self) -> bool:
        """Check if output is being redirected."""
        return self._is_redirected

    def print_markdown(
        self,
        content: str,
        json_data: Optional[Dict[str, Any]] = None,
        csv_data: Optional[List[List[str]]] = None,
        json_output: bool = False,
        csv_output: bool = False,
    ) -> None:
        """
        Print content in the appropriate format.

        Args:
            content: Markdown content to display
            json_data: Data to output as JSON (if json_output=True)
            csv_data: Data to output as CSV (if csv_output=True)
            json_output: Whether to output JSON
            csv_output: Whether to output CSV
        """
        if json_output and json_data is not None:
            print(json.dumps(json_data, indent=2, default=str))
        elif csv_output and csv_data is not None:
            writer = csv.writer(sys.stdout)
            for row in csv_data:
                writer.writerow(row)
        else:
            # Markdown output
            if self._is_redirected:
                # Plain markdown for redirected output
                print(content)
            else:
                # Rich rendering for interactive output
                self._console.print(Markdown(content))

    def print_json(self, data: Dict[str, Any]) -> None:
        """Print data as JSON."""
        print(json.dumps(data, indent=2, default=str))

    def print_csv(self, rows: List[List[str]]) -> None:
        """Print data as CSV."""
        writer = csv.writer(sys.stdout)
        for row in rows:
            writer.writerow(row)

    def print_table_markdown(
        self,
        title: str,
        headers: List[str],
        rows: List[List[str]],
        subtitle: Optional[str] = None,
    ) -> str:
        """
        Generate a markdown table.

        Args:
            title: Table title
            headers: Column headers
            rows: Table rows
            subtitle: Optional subtitle

        Returns:
            Markdown table as string
        """
        if subtitle:
            content = f"# {title}\n\n{subtitle}\n\n"
        else:
            content = f"# {title}\n\n"

        # Add table headers
        header_row = "| " + " | ".join(headers) + " |"
        separator_row = "|" + "|".join(["-" * (len(h) + 2) for h in headers]) + "|"

        content += header_row + "\n" + separator_row + "\n"

        # Add table rows
        for row in rows:
            content += "| " + " | ".join(str(cell) for cell in row) + " |\n"

        return content

    def print_sectioned_markdown(
        self, title: str, sections: Dict[str, Union[str, List[str]]]
    ) -> str:
        """
        Generate sectioned markdown content.

        Args:
            title: Document title
            sections: Dictionary of section names to content

        Returns:
            Markdown content as string
        """
        content = f"# {title}\n\n"

        for section_name, section_content in sections.items():
            content += f"## {section_name}\n\n"

            if isinstance(section_content, list):
                if section_content and section_content[0].startswith("|"):
                    # It's a table
                    content += "\n".join(section_content) + "\n\n"
                else:
                    # It's a list
                    for item in section_content:
                        content += f"- {item}\n"
                    content += "\n"
            else:
                # It's a string
                content += str(section_content) + "\n\n"

        return content


# Global output manager instance
output_manager = OutputManager()


def get_output_manager() -> OutputManager:
    """Get the global output manager instance."""
    return output_manager
