"""
Progress indicators and status reporting for ploTTY operations.

This module provides progress bars, status updates, and user feedback
for long-running operations like planning, optimization, and plotting.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Callable, Generator, Optional

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)


class PlottyProgress:
    """
    Progress indicator system for ploTTY operations.

    Provides consistent progress bars and status updates across
    all ploTTY commands and operations.
    """

    def __init__(self, console: Optional[Console] = None) -> None:
        self.console = console or Console()
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.console,
        )

    @contextmanager
    def task(
        self, description: str, total: Optional[int] = None, show_spinner: bool = True
    ) -> Generator[Callable[[int], None], None, None]:
        """
        Context manager for a progress task.

        Args:
            description: Task description
            total: Total number of steps (None for indeterminate)
            show_spinner: Whether to show spinner for indeterminate progress

        Yields:
            Update function that takes the current progress
        """
        with self._progress:
            task_id = self._progress.add_task(description, total=total, visible=True)

            def update(progress: int = 1, description: Optional[str] = None) -> None:
                """Update the progress bar."""
                if description:
                    self._progress.update(
                        task_id, description=description, advance=progress
                    )
                else:
                    self._progress.update(task_id, advance=progress)

            try:
                yield update
            finally:
                self._progress.update(task_id, completed=total or 100)

    @contextmanager
    def spinner(self, description: str) -> Generator[None, None, None]:
        """
        Context manager for a spinner animation.

        Args:
            description: Description of the operation
        """
        with self._progress:
            task_id = self._progress.add_task(description, total=None)
            try:
                yield
            finally:
                self._progress.update(task_id, completed=1)

    def show_status(self, message: str, style: str = "info") -> None:
        """
        Show a status message.

        Args:
            message: Status message to display
            style: Message style (info, success, warning, error)
        """
        style_map = {
            "info": "blue",
            "success": "green",
            "warning": "yellow",
            "error": "red",
        }

        color = style_map.get(style, "white")
        self.console.print(f"[{color}]{message}[/{color}]")


class LayerProgress:
    """
    Specialized progress indicator for layer operations.

    Tracks progress through multiple layers with individual status
    for each layer being processed.
    """

    def __init__(self, console: Optional[Console] = None) -> None:
        self.console = console or Console()
        self.progress = PlottyProgress(console)

    @contextmanager
    def process_layers(
        self, layer_count: int, operation: str = "Processing"
    ) -> Generator[Callable[[int, str], None], None, None]:
        """
        Context manager for processing multiple layers.

        Args:
            layer_count: Total number of layers to process
            operation: Description of the operation being performed

        Yields:
            Update function that takes (layer_index, status_message)
        """
        with self.progress.task(
            description=f"{operation} layers", total=layer_count
        ) as update:

            def update_layer(layer_idx: int, status: str) -> None:
                """Update progress for a specific layer."""
                update(1, f"{operation} layer {layer_idx + 1}/{layer_count}: {status}")

            try:
                yield update_layer
            finally:
                self.progress.show_status(
                    f"Completed {operation.lower()} {layer_count} layers", "success"
                )


class VpypeProgress:
    """
    Progress tracking for vpype operations.

    Provides progress feedback for vpype commands like optimization,
    simplification, and other processing steps.
    """

    def __init__(self, console: Optional[Console] = None) -> None:
        self.console = console or Console()
        self.progress = PlottyProgress(console)

    @contextmanager
    def optimize_geometry(
        self, segment_count: int
    ) -> Generator[Callable[[int], None], None, None]:
        """
        Progress tracking for geometry optimization.

        Args:
            segment_count: Number of segments to process

        Yields:
            Update function that takes the current progress
        """
        with self.progress.task(
            description="Optimizing geometry", total=segment_count
        ) as update:
            yield update

    @contextmanager
    def process_layers(
        self, layer_count: int
    ) -> Generator[Callable[[int, str], None], None, None]:
        """
        Progress tracking for layer processing.

        Args:
            layer_count: Number of layers to process

        Yields:
            Update function that takes (layer_index, operation)
        """
        with self.progress.task(
            description="Processing layers", total=layer_count
        ) as update:

            def update_layer(layer_idx: int, operation: str) -> None:
                """Update progress for layer processing."""
                update(1, f"Layer {layer_idx + 1}/{layer_count}: {operation}")

            yield update_layer

    def show_optimization_result(self, before: int, after: int) -> None:
        """
        Show optimization results.

        Args:
            before: Number of segments before optimization
            after: Number of segments after optimization
        """
        reduction = ((before - after) / before) * 100 if before > 0 else 0
        self.progress.show_status(
            f"Optimized: {before:,} → {after:,} segments ({reduction:.1f}% reduction)",
            "success",
        )


# Global progress instance
progress = PlottyProgress()
layer_progress = LayerProgress()
vpype_progress = VpypeProgress()


@contextmanager
def progress_task(
    description: str, total: Optional[int] = None
) -> Generator[Callable[[int], None], None, None]:
    """
    Convenience function for creating a progress task.

    Args:
        description: Task description
        total: Total number of steps

    Yields:
        Update function
    """
    with progress.task(description, total) as update:
        yield update


@contextmanager
def spinner_task(description: str) -> Generator[None, None, None]:
    """
    Convenience function for creating a spinner task.

    Args:
        description: Description of the operation
    """
    with progress.spinner(description):
        yield


def show_status(message: str, style: str = "info") -> None:
    """
    Convenience function for showing status messages.

    Args:
        message: Status message
        style: Message style
    """
    progress.show_status(message, style)
