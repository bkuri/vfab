#!/usr/bin/env python3
"""
ploTTY Session Manager TUI Demo

A complete, self-contained demonstration of the ploTTY session management TUI.
This version includes all components in a single file to avoid import issues.

Run with: python plotty_tui_demo.py
"""

import asyncio
import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widgets import (
    Button,
    Digits,
    Label,
    ProgressBar,
    Static,
    DataTable,
    Header,
    Footer,
)
from textual.binding import Binding

# ploTTY FSM states
FSM_STATES = [
    "NEW",
    "QUEUED",
    "ANALYZED",
    "OPTIMIZED",
    "READY",
    "ARMED",
    "PLOTTING",
    "PAUSED",
    "COMPLETED",
    "ABORTED",
    "FAILED",
]

ACTIVE_STATES = ["ARMED", "PLOTTING", "PAUSED"]
COMPLETED_STATES = ["COMPLETED", "ABORTED", "FAILED"]


class SessionDisplay(Digits):
    """A widget to display session time and progress."""

    start_time = reactive(0.0)
    time = reactive(0.0)
    total = reactive(0.0)
    progress = reactive(0.0)
    current_layer = reactive("")
    total_layers = reactive(0)

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.update_timer = self.set_interval(1 / 60, self.update_time, pause=True)

    def update_time(self) -> None:
        """Method to update time to current."""
        self.time = self.total + (time.time() - self.start_time)

    def watch_time(self, time: float) -> None:
        """Called when the time attribute changes."""
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        time_str = f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}"

        if self.current_layer and self.total_layers > 0:
            self.update(f"{time_str} L{self.current_layer}/{self.total_layers}")
        else:
            self.update(time_str)

    def start(self) -> None:
        """Method to start (or resume) time updating."""
        self.start_time = time.time()
        self.update_timer.resume()

    def stop(self):
        """Method to stop the time display updating."""
        self.update_timer.pause()
        self.total += time.time() - self.start_time
        self.time = self.total

    def reset(self):
        """Method to reset the time display to zero."""
        self.total = 0
        self.time = 0
        self.progress = 0.0
        self.current_layer = ""
        self.total_layers = 0


class SessionWidget(Vertical):
    """A plotting session widget adapted from stopwatch."""

    def __init__(
        self,
        device_name: str = "Axidraw #1",
        device_id: str = "axidraw-1",
        job_name: str = "",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.device_name = device_name
        self.device_id = device_id
        self.job_name = job_name
        self._state = "NEW"

    # Reactive properties
    state = reactive("NEW")
    job_name = reactive("")
    progress = reactive(0.0)
    eta_seconds = reactive(0)

    def compose(self) -> ComposeResult:
        """Create child widgets of a session widget."""
        with Horizontal(classes="session-header"):
            yield Label(f"Device: {self.device_name}", classes="device-name")
            yield Label(
                self._get_state_display(), classes="state-label", id="state-label"
            )

        with Horizontal(classes="session-info"):
            yield Label(
                f"Job: {self.job_name or 'None'}", classes="job-name", id="job-name"
            )
            yield ProgressBar(total=100, show_eta=True, classes="progress-bar")

        yield SessionDisplay(classes="session-display")

        with Horizontal(classes="session-controls"):
            yield Button("Queue", id="queue", variant="primary")
            yield Button("Start", id="start", variant="success")
            yield Button("Pause", id="pause", variant="warning")
            yield Button("Abort", id="abort", variant="error")
            yield Button("Reset", id="reset")

    def on_mount(self) -> None:
        """Initialize the widget when mounted."""
        self._update_button_visibility()
        self._update_classes()

    def _get_state_display(self) -> str:
        """Get human-readable state display."""
        state_colors = {
            "NEW": "🆕 NEW",
            "QUEUED": "⏳ QUEUED",
            "ANALYZED": "📊 ANALYZED",
            "OPTIMIZED": "⚡ OPTIMIZED",
            "READY": "✅ READY",
            "ARMED": "🎯 ARMED",
            "PLOTTING": "🖊️ PLOTTING",
            "PAUSED": "⏸️ PAUSED",
            "COMPLETED": "✨ COMPLETED",
            "ABORTED": "🛑 ABORTED",
            "FAILED": "❌ FAILED",
        }
        return state_colors.get(self._state, f"❓ {self._state}")

    def _update_button_visibility(self) -> None:
        """Update button visibility based on current state."""
        buttons = {
            "queue": self._state in ["NEW", "COMPLETED", "ABORTED", "FAILED"],
            "start": self._state in ["READY", "ARMED", "PAUSED"],
            "pause": self._state == "PLOTTING",
            "abort": self._state in ["QUEUED", "ARMED", "PLOTTING", "PAUSED"],
            "reset": self._state in COMPLETED_STATES,
        }

        for button_id, should_show in buttons.items():
            try:
                button = self.query_one(f"#{button_id}")
                button.display = should_show
            except:
                pass

    def _update_classes(self) -> None:
        """Update CSS classes based on state."""
        # Remove state classes
        for state in FSM_STATES:
            self.remove_class(f"state-{state.lower()}")

        # Add current state class
        self.add_class(f"state-{self._state.lower()}")

        # Add generic status classes
        if self._state in ACTIVE_STATES:
            self.add_class("active")
        elif self._state in COMPLETED_STATES:
            self.add_class("completed")
        else:
            self.add_class("idle")

    def watch_state(self, state: str) -> None:
        """Called when the state attribute changes."""
        self._state = state
        self._update_button_visibility()
        self._update_classes()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        session_display = self.query_one(SessionDisplay)

        if button_id == "start":
            if self._state in ["READY", "ARMED"]:
                self.state = "PLOTTING"
                session_display.start()
            elif self._state == "PAUSED":
                self.state = "PLOTTING"
                session_display.start()

        elif button_id == "pause":
            if self._state == "PLOTTING":
                self.state = "PAUSED"
                session_display.stop()

        elif button_id == "abort":
            if self._state in ["QUEUED", "ARMED", "PLOTTING", "PAUSED"]:
                self.state = "ABORTED"
                session_display.stop()

        elif button_id == "queue":
            if self._state in ["NEW", "COMPLETED", "ABORTED", "FAILED"]:
                self.state = "QUEUED"

        elif button_id == "reset":
            if self._state in COMPLETED_STATES:
                self.state = "NEW"
                session_display.reset()
                self.job_name = ""
                self.progress = 0.0


class JobQueue(Vertical):
    """Job queue management widget."""

    def compose(self) -> ComposeResult:
        yield Label("Job Queue", classes="queue-header")
        yield DataTable(id="job-table", classes="job-table")

    def on_mount(self) -> None:
        """Initialize the job table."""
        table = self.query_one("#job-table", DataTable)
        table.add_columns("ID", "Name", "State", "Device", "Progress")


class DeviceStatus(Vertical):
    """Device status overview widget."""

    def compose(self) -> ComposeResult:
        yield Label("Device Status", classes="device-header")
        yield Static(
            "Active: 0 | Idle: 0 | Total: 0",
            id="device-summary",
            classes="device-summary",
        )


class PlottyTUIApp(App):
    """Main ploTTY session manager TUI application."""

    CSS = """
    SessionWidget {
        background: $boost;
        height: auto;
        min-height: 12;
        margin: 1;
        padding: 1;
        border: solid $panel;
    }

    .session-header {
        height: 3;
        margin-bottom: 1;
    }

    .device-name {
        width: 1fr;
        text-style: bold;
        color: $foreground;
    }

    .state-label {
        width: 1fr;
        text-align: right;
        color: $foreground-muted;
    }

    .session-info {
        height: 3;
        margin-bottom: 1;
    }

    .job-name {
        width: 2fr;
        color: $text;
    }

    .progress-bar {
        width: 1fr;
        margin-left: 1;
    }

    .session-display {
        text-align: center;
        color: $foreground-muted;
        height: 3;
        margin-bottom: 1;
    }

    .session-controls {
        height: 3;
    }

    .session-controls Button {
        width: 1fr;
        margin: 0 1 0 0;
    }

    .session-controls Button:last-child {
        margin-right: 0;
    }

    /* State-specific styling */
    SessionWidget.state-plotting {
        background: $success;
        color: $text;
    }

    SessionWidget.state-paused {
        background: $warning;
        color: $text;
    }

    SessionWidget.state-completed {
        background: $success-muted;
    }

    SessionWidget.state-failed {
        background: $error;
        color: $text;
    }

    /* Active sessions styling */
    SessionWidget.active {
        background: $success;
    }

    #main-container {
        height: 100%;
    }

    #sessions-panel {
        width: 2fr;
        height: 100%;
        padding: 1;
    }

    #info-panel {
        width: 1fr;
        height: 100%;
        padding: 1;
    }

    .sessions-scroll {
        height: 1fr;
        border: solid $primary;
        background: $surface;
    }

    .panel-header {
        text-align: center;
        text-style: bold;
        color: $accent;
        height: 3;
        margin: 0 0 1 0;
    }

    .queue-header, .device-header {
        text-align: center;
        text-style: bold;
        color: $accent;
        height: 3;
        margin: 0 0 1 0;
    }

    JobQueue {
        background: $surface;
        height: 1fr;
        margin-bottom: 1;
        padding: 1;
        border: solid $panel;
    }

    DeviceStatus {
        background: $surface;
        height: 8;
        padding: 1;
        border: solid $panel;
    }

    .device-summary {
        text-align: center;
        color: $foreground;
        height: 3;
    }
    """

    BINDINGS = [
        Binding("d", "toggle_dark", "Toggle dark mode"),
        Binding("q", "quit", "Quit"),
        Binding("a", "add_session", "Add Session"),
        Binding("r", "remove_session", "Remove Session"),
        Binding("s", "show_queue", "Show Queue"),
        Binding("f5", "refresh", "Refresh"),
        Binding("space", "simulate_job", "Simulate Job"),
    ]

    def compose(self) -> ComposeResult:
        """Create the main application layout."""
        yield Header()

        with Horizontal(id="main-container"):
            # Left panel - Device sessions
            with Vertical(id="sessions-panel"):
                yield Label("Active Sessions", classes="panel-header")
                yield VerticalScroll(id="sessions-container", classes="sessions-scroll")

            # Right panel - Queue and status
            with Vertical(id="info-panel"):
                yield JobQueue(classes="queue-widget")
                yield DeviceStatus(classes="device-widget")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the application."""
        self._add_default_sessions()
        self._update_device_summary()
        self._start_simulation()

    def _add_default_sessions(self) -> None:
        """Add default demo sessions."""
        default_sessions = [
            {
                "device_name": "Axidraw #1",
                "device_id": "axidraw-1",
                "job_name": "mandala.svg",
            },
            {"device_name": "Axidraw #2", "device_id": "axidraw-2", "job_name": ""},
            {
                "device_name": "Axidraw #3",
                "device_id": "axidraw-3",
                "job_name": "geometric-pattern.svg",
            },
        ]

        for session_data in default_sessions:
            self._create_session(**session_data)

    def _create_session(
        self, device_name: str, device_id: str, job_name: str = ""
    ) -> None:
        """Create a new session widget."""
        session = SessionWidget(
            device_name=device_name,
            device_id=device_id,
            job_name=job_name,
            id=f"session-{device_id}",
        )

        sessions_container = self.query_one("#sessions-container")
        sessions_container.mount(session)

        # Set initial state based on job presence
        if job_name:
            session.state = "READY"
        else:
            session.state = "NEW"

        if not hasattr(self, "sessions"):
            self.sessions = []
        self.sessions.append(session)

    def _update_device_summary(self) -> None:
        """Update the device status summary."""
        if not hasattr(self, "sessions"):
            return

        active_count = sum(1 for s in self.sessions if s.state in ACTIVE_STATES)
        idle_count = len(self.sessions) - active_count
        total_count = len(self.sessions)

        try:
            summary = self.query_one("#device-summary", Static)
            summary.update(
                f"Active: {active_count} | Idle: {idle_count} | Total: {total_count}"
            )
        except:
            pass

    def _update_job_table(self) -> None:
        """Update the job queue table."""
        if not hasattr(self, "sessions"):
            return

        try:
            table = self.query_one("#job-table", DataTable)
            table.clear()

            for session in self.sessions:
                if session.job_name and session.state != "NEW":
                    table.add_row(
                        session.device_id,
                        session.job_name,
                        session.state,
                        session.device_name,
                        f"{session.progress:.1f}%",
                    )
        except:
            pass

    def action_add_session(self) -> None:
        """Add a new session."""
        if not hasattr(self, "sessions"):
            self.sessions = []

        device_num = len(self.sessions) + 1
        device_id = f"axidraw-{device_num}"
        device_name = f"Axidraw #{device_num}"

        self._create_session(device_name, device_id)
        self._update_device_summary()

    def action_remove_session(self) -> None:
        """Remove the last session."""
        if hasattr(self, "sessions") and self.sessions:
            last_session = self.sessions.pop()
            last_session.remove()
            self._update_device_summary()

    def action_show_queue(self) -> None:
        """Show/hide the job queue."""
        queue_widget = self.query_one(JobQueue)
        queue_widget.display = not queue_widget.display

    def action_refresh(self) -> None:
        """Refresh all displays."""
        self._update_device_summary()
        self._update_job_table()

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_simulate_job(self) -> None:
        """Simulate a job on the first idle device."""
        if not hasattr(self, "sessions"):
            return

        idle_sessions = [s for s in self.sessions if s.state == "NEW"]
        if idle_sessions:
            session = idle_sessions[0]
            session.job_name = f"simulated-{int(time.time())}.svg"
            asyncio.create_task(self._simulate_session_workflow(session))

    async def _simulate_session_workflow(self, session: SessionWidget) -> None:
        """Simulate the complete session workflow."""
        workflow_steps = [
            ("QUEUED", 1.0),
            ("ANALYZED", 2.0),
            ("OPTIMIZED", 2.0),
            ("READY", 1.0),
            ("ARMED", 1.0),
        ]

        for state, duration in workflow_steps:
            session.state = state
            self._update_job_table()
            await asyncio.sleep(duration)

        # Start plotting
        session.state = "PLOTTING"
        session_display = session.query_one(SessionDisplay)
        session_display.start()
        self._update_job_table()

        # Simulate plotting progress
        for progress in range(20, 101, 20):
            session.progress = progress
            await asyncio.sleep(2.0)

        # Complete
        session.state = "COMPLETED"
        session_display.stop()
        self._update_job_table()

    def _start_simulation(self) -> None:
        """Start automatic simulation."""

        async def simulation_loop():
            while True:
                await asyncio.sleep(10.0)  # Every 10 seconds
                self.action_simulate_job()

        # Don't await the simulation loop, let it run in background


def main():
    """Run the ploTTY TUI demo."""
    print("Starting ploTTY Session Manager TUI Demo")
    print("=" * 50)
    print("Keyboard shortcuts:")
    print("- 'a': Add new session")
    print("- 'r': Remove last session")
    print("- 's': Toggle queue visibility")
    print("- 'space': Simulate new job")
    print("- 'd': Toggle dark mode")
    print("- 'F5': Refresh displays")
    print("- 'q': Quit")
    print("=" * 50)
    print("The demo will automatically simulate jobs every 10 seconds.")
    print("=" * 50)

    app = PlottyTUIApp()
    app.run()


if __name__ == "__main__":
    main()
