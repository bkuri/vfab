"""
Output formatting utilities for vfab status commands.

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
        hierarchical_csv_data: Optional[List[Dict[str, Any]]] = None,
        tabular_csv_data: Optional[Dict[str, Any]] = None,
        json_output: bool = False,
        csv_output: bool = False,
    ) -> None:
        """
        Print content in the appropriate format.

        Args:
            content: Markdown content to display
            json_data: Data to output as JSON (if json_output=True)
            csv_data: Legacy CSV data (if csv_output=True)
            hierarchical_csv_data: Hierarchical CSV data (if csv_output=True)
            tabular_csv_data: Tabular CSV data with headers and rows (if csv_output=True)
            json_output: Whether to output JSON
            csv_output: Whether to output CSV
        """
        if json_output and json_data is not None:
            print(json.dumps(json_data, indent=2, default=str))
        elif csv_output:
            if hierarchical_csv_data is not None:
                self.print_hierarchical_csv(hierarchical_csv_data)
            if tabular_csv_data is not None:
                # Print blank line to separate sections
                print()
                headers = tabular_csv_data.get("headers", [])
                rows = tabular_csv_data.get("rows", [])
                self.print_tabular_csv(rows, headers)
            elif csv_data is not None:
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

    def print_hierarchical_csv(
        self,
        data: List[Dict[str, Any]],
        section_col: str = "Section",
        category_col: str = "Category",
        item_col: str = "Item",
        value_col: str = "Value",
    ) -> None:
        """
        Print hierarchical data as unified CSV.

        Args:
            data: List of dictionaries with hierarchical data
            section_col: Name of section column
            category_col: Name of category column
            item_col: Name of item column
            value_col: Name of value column
        """
        writer = csv.writer(sys.stdout)

        # Write header
        header = [section_col, category_col, item_col, value_col]
        writer.writerow(header)

        # Write data rows
        for row_data in data:
            section = row_data.get("section", "")
            category = row_data.get("category", "")
            item = row_data.get("item", "")
            value = row_data.get("value", "")

            writer.writerow([section, category, item, value])

    def print_tabular_csv(
        self,
        data: List[Dict[str, Any]],
        headers: List[str],
    ) -> None:
        """
        Print tabular data as CSV.

        Args:
            data: List of dictionaries with tabular data
            headers: List of column headers
        """
        writer = csv.writer(sys.stdout)

        # Write header
        writer.writerow(headers)

        # Write data rows
        for row_data in data:
            row = [row_data.get(header, "") for header in headers]
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
