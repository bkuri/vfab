#!/usr/bin/env python3
"""
ploTTY Session Manager TUI with Tabbed Interface

Enhanced version with TabbedContent containing:
- Dashboard tab (overview of all sessions)
- Individual session detail tabs
- Real-time updates and navigation
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
    TabbedContent,
    TabPane,
)
from textual.binding import Binding
from textual.message import Message

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
        """Event handler called when widget is added to app."""
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
    """A compact plotting session widget for dashboard view."""

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
            yield Label(self._get_state_display(), classes="state-label")

        with Horizontal(classes="session-info"):
            yield Label(f"Job: {self.job_name or 'None'}", classes="job-name")
            yield ProgressBar(total=100, show_eta=False, classes="progress-bar")

        with Horizontal(classes="session-controls"):
            yield Button("Details", id=f"details-{self.device_id}", variant="primary")
            yield Button("Start", id=f"start-{self.device_id}", variant="success")
            yield Button("Pause", id=f"pause-{self.device_id}", variant="warning")
            yield Button("Abort", id=f"abort-{self.device_id}", variant="error")

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
            f"start-{self.device_id}": self._state in ["READY", "ARMED", "PAUSED"],
            f"pause-{self.device_id}": self._state == "PLOTTING",
            f"abort-{self.device_id}": self._state
            in ["QUEUED", "ARMED", "PLOTTING", "PAUSED"],
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

        if button_id == f"start-{self.device_id}":
            if self._state in ["READY", "ARMED"]:
                self.state = "PLOTTING"
            elif self._state == "PAUSED":
                self.state = "PLOTTING"

        elif button_id == f"pause-{self.device_id}":
            if self._state == "PLOTTING":
                self.state = "PAUSED"

        elif button_id == f"abort-{self.device_id}":
            if self._state in ["QUEUED", "ARMED", "PLOTTING", "PAUSED"]:
                self.state = "ABORTED"

        elif button_id and button_id.startswith("details-"):
            # Post message to open details tab
            self.post_message(SessionDetailsRequested(self.device_id))


class SessionDetailsRequested(Message):
    """Message sent when session details are requested."""

    def __init__(self, device_id: str) -> None:
        self.device_id = device_id
        super().__init__()


class SessionDetailView(TabPane):
    """Detailed view for a single session."""

    def __init__(self, device_id: str, device_name: str, **kwargs):
        super().__init__(title=f"{device_name} Details", **kwargs)
        self.device_id = device_id
        self.device_name = device_name
        self.session_data = {}

    def compose(self) -> ComposeResult:
        """Create detailed session view."""
        yield Label(f"Device: {self.device_name}", classes="detail-header")
        yield Label(f"Device ID: {self.device_id}", classes="detail-subheader")

        with Vertical(classes="detail-section"):
            yield Label("Session Information", classes="section-title")
            yield Label("State: NEW", id="detail-state", classes="detail-field")
            yield Label("Job: None", id="detail-job", classes="detail-field")
            yield Label("Progress: 0%", id="detail-progress", classes="detail-field")

        with Vertical(classes="detail-section"):
            yield Label("Timing", classes="section-title")
            yield Label(
                "Duration: 00:00:00.00", id="detail-duration", classes="detail-field"
            )
            yield Label("ETA: --:--:--", id="detail-eta", classes="detail-field")

        with Vertical(classes="detail-section"):
            yield Label("Layer Information", classes="section-title")
            yield Label(
                "Current: --", id="detail-current-layer", classes="detail-field"
            )
            yield Label("Total: --", id="detail-total-layers", classes="detail-field")

        with Vertical(classes="detail-section"):
            yield Label("Controls", classes="section-title")
            with Horizontal(classes="detail-controls"):
                yield Button("Queue Job", id="detail-queue", variant="primary")
                yield Button("Start Plotting", id="detail-start", variant="success")
                yield Button("Pause", id="detail-pause", variant="warning")
                yield Button("Abort", id="detail-abort", variant="error")
                yield Button("Reset", id="detail-reset", variant="default")

        with Vertical(classes="detail-section"):
            yield Label("Session Log", classes="section-title")
            yield VerticalScroll(id="detail-log", classes="log-view")

    def update_session_data(self, **kwargs) -> None:
        """Update the detailed session information."""
        try:
            if "state" in kwargs:
                state_label = self.query_one("#detail-state", Label)
                state_label.update(f"State: {kwargs['state']}")
            if "job_name" in kwargs:
                job_label = self.query_one("#detail-job", Label)
                job_label.update(f"Job: {kwargs['job_name'] or 'None'}")
            if "progress" in kwargs:
                progress_label = self.query_one("#detail-progress", Label)
                progress_label.update(f"Progress: {kwargs['progress']:.1f}%")
            if "eta_seconds" in kwargs:
                eta = kwargs["eta_seconds"]
                eta_label = self.query_one("#detail-eta", Label)
                if eta > 0:
                    minutes, seconds = divmod(eta, 60)
                    hours, minutes = divmod(minutes, 60)
                    eta_label.update(
                        f"ETA: {hours:02.0f}:{minutes:02.0f}:{seconds:02.0f}"
                    )
                else:
                    eta_label.update("ETA: --:--:--")
            if "current_layer" in kwargs:
                layer_label = self.query_one("#detail-current-layer", Label)
                layer_label.update(f"Current: {kwargs['current_layer']}")
            if "total_layers" in kwargs:
                total_label = self.query_one("#detail-total-layers", Label)
                total_label.update(f"Total: {kwargs['total_layers']}")
        except:
            pass

    def add_log_entry(self, message: str) -> None:
        """Add an entry to the session log."""
        try:
            log_view = self.query_one("#detail-log", VerticalScroll)
            timestamp = time.strftime("%H:%M:%S")
            log_entry = Label(f"[{timestamp}] {message}", classes="log-entry")
            log_view.mount(log_entry)
            log_view.scroll_end()
        except:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle detail view button presses."""
        # Post control messages back to main app
        if event.button.id == "detail-queue":
            self.post_message(SessionControlRequested(self.device_id, "queue"))
        elif event.button.id == "detail-start":
            self.post_message(SessionControlRequested(self.device_id, "start"))
        elif event.button.id == "detail-pause":
            self.post_message(SessionControlRequested(self.device_id, "pause"))
        elif event.button.id == "detail-abort":
            self.post_message(SessionControlRequested(self.device_id, "abort"))
        elif event.button.id == "detail-reset":
            self.post_message(SessionControlRequested(self.device_id, "reset"))


class SessionControlRequested(Message):
    """Message sent when session control is requested from detail view."""

    def __init__(self, device_id: str, action: str) -> None:
        self.device_id = device_id
        self.action = action
        super().__init__()


class DashboardTab(TabPane):
    """Dashboard tab showing overview of all sessions."""

    def compose(self) -> ComposeResult:
        """Create dashboard content."""
        yield Label("Session Dashboard", classes="dashboard-title")

        with Horizontal(classes="dashboard-stats"):
            yield Static("Active: 0", id="active-count", classes="stat-box")
            yield Static("Idle: 0", id="idle-count", classes="stat-box")
            yield Static("Total: 0", id="total-count", classes="stat-box")

        with Vertical(classes="sessions-container"):
            yield Label("Active Sessions", classes="section-title")
            yield VerticalScroll(id="sessions-scroll", classes="sessions-scroll")

    def update_stats(self, active: int, idle: int, total: int) -> None:
        """Update dashboard statistics."""
        try:
            active_label = self.query_one("#active-count", Static)
            active_label.update(f"Active: {active}")
            idle_label = self.query_one("#idle-count", Static)
            idle_label.update(f"Idle: {idle}")
            total_label = self.query_one("#total-count", Static)
            total_label.update(f"Total: {total}")
        except:
            pass


class JobQueue(Vertical):
    """Job queue management widget."""

    def compose(self) -> ComposeResult:
        yield Label("Job Queue", classes="queue-header")
        yield DataTable(id="job-table", classes="job-table")

    def on_mount(self) -> None:
        """Initialize the job table."""
        table = self.query_one("#job-table", DataTable)
        table.add_columns("ID", "Name", "State", "Device", "Progress")


class PlottyTabbedTUIApp(App):
    """ploTTY session manager TUI with tabbed interface."""

    CSS = """
    /* Dashboard Styles */
    .dashboard-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        height: 3;
    }

    .dashboard-stats {
        height: 5;
        margin: 1 0;
    }

    .stat-box {
        width: 1fr;
        height: 3;
        margin: 0 1;
        background: $surface;
        border: solid $panel;
        text-align: center;
        content-align: center middle;
        text-style: bold;
    }

    .sessions-container {
        height: 1fr;
    }

    .section-title {
        text-style: bold;
        color: $accent;
        height: 2;
        margin: 1 0 0 0;
    }

    .sessions-scroll {
        height: 1fr;
        border: solid $primary;
        background: $surface;
    }

    /* Session Widget Styles */
    SessionWidget {
        background: $boost;
        height: auto;
        min-height: 10;
        margin: 1;
        padding: 1;
        border: solid $panel;
    }

    .session-header {
        height: 2;
        margin-bottom: 1;
    }

    .device-name {
        width: 2fr;
        text-style: bold;
        color: $foreground;
    }

    .state-label {
        width: 1fr;
        text-align: right;
        color: $foreground-muted;
    }

    .session-info {
        height: 2;
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

    SessionWidget.state-plotting .device-name,
    SessionWidget.state-plotting .state-label,
    SessionWidget.state-plotting .job-name {
        color: $text;
    }

    SessionWidget.state-paused {
        background: $warning;
        color: $text;
    }

    SessionWidget.state-paused .device-name,
    SessionWidget.state-paused .state-label,
    SessionWidget.state-paused .job-name {
        color: $text;
    }

    SessionWidget.state-completed {
        background: $success-muted;
    }

    SessionWidget.state-failed {
        background: $error;
        color: $text;
    }

    SessionWidget.state-failed .device-name,
    SessionWidget.state-failed .state-label,
    SessionWidget.state-failed .job-name {
        color: $text;
    }

    /* Detail View Styles */
    .detail-header {
        text-style: bold;
        color: $accent;
        height: 2;
    }

    .detail-subheader {
        color: $foreground-muted;
        height: 2;
    }

    .detail-section {
        margin: 1 0;
        padding: 1;
        background: $surface;
        border: solid $panel;
    }

    .detail-field {
        height: 2;
        margin: 0 0 0 1;
    }

    .detail-controls {
        margin: 1 0 0 0;
    }

    .detail-controls Button {
        width: 1fr;
        margin: 0 1 0 0;
    }

    .detail-controls Button:last-child {
        margin-right: 0;
    }

    .log-view {
        height: 10;
        background: $panel;
        border: solid $surface;
    }

    .log-entry {
        margin: 0 0 0 1;
        color: $text;
    }

    /* Job Queue Styles */
    JobQueue {
        background: $surface;
        height: 1fr;
        margin: 1;
        padding: 1;
        border: solid $panel;
    }

    .queue-header {
        text-align: center;
        text-style: bold;
        color: $accent;
        height: 3;
        margin: 0 0 1 0;
    }

    .job-table {
        height: 1fr;
    }

    /* TabbedContent adjustments */
    TabbedContent {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("d", "toggle_dark", "Toggle dark mode"),
        Binding("q", "quit", "Quit"),
        Binding("a", "add_session", "Add Session"),
        Binding("r", "remove_session", "Remove Session"),
        Binding("1", "focus_tab_1", "Dashboard"),
        Binding("2-9", "focus_tab_n", "Session Tab"),
        Binding("ctrl+tab", "next_tab", "Next Tab"),
        Binding("ctrl+shift+tab", "previous_tab", "Previous Tab"),
        Binding("space", "simulate_job", "Simulate Job"),
    ]

    def compose(self) -> ComposeResult:
        """Create the main application layout."""
        yield Header()

        with TabbedContent(id="main-tabs"):
            with DashboardTab(title="📊 Dashboard", id="dashboard-tab"):
                yield JobQueue(classes="queue-widget")

            # Session detail tabs will be added dynamically

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the application."""
        self.sessions = []
        self.detail_tabs = {}
        self._add_default_sessions()
        self._update_dashboard()
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
        """Create a new session and corresponding detail tab."""
        # Create session widget for dashboard
        session = SessionWidget(
            device_name=device_name,
            device_id=device_id,
            job_name=job_name,
            id=f"session-{device_id}",
        )

        # Add to dashboard
        dashboard = self.query_one("#dashboard-tab")
        sessions_scroll = dashboard.query_one("#sessions-scroll")
        sessions_scroll.mount(session)

        # Create detail tab
        detail_tab = SessionDetailView(
            device_id=device_id, device_name=device_name, id=f"detail-{device_id}"
        )

        tabbed_content = self.query_one(TabbedContent)
        tabbed_content.mount(detail_tab)

        # Set initial state
        if job_name:
            session.state = "READY"
            detail_tab.update_session_data(state="READY", job_name=job_name)
        else:
            session.state = "NEW"
            detail_tab.update_session_data(state="NEW")

        # Store references
        self.sessions.append(session)
        self.detail_tabs[device_id] = detail_tab

        # Add initial log entry
        detail_tab.add_log_entry(f"Session created for {device_name}")

    def _update_dashboard(self) -> None:
        """Update dashboard statistics and job table."""
        if not self.sessions:
            return

        active_count = sum(1 for s in self.sessions if s.state in ACTIVE_STATES)
        idle_count = len(self.sessions) - active_count
        total_count = len(self.sessions)

        # Update stats
        dashboard = self.query_one("#dashboard-tab", DashboardTab)
        dashboard.update_stats(active_count, idle_count, total_count)

        # Update job table
        try:
            job_queue = dashboard.query_one(JobQueue)
            table = job_queue.query_one("#job-table", DataTable)
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
        device_num = len(self.sessions) + 1
        device_id = f"axidraw-{device_num}"
        device_name = f"Axidraw #{device_num}"

        self._create_session(device_name, device_id)
        self._update_dashboard()

    def action_remove_session(self) -> None:
        """Remove the last session."""
        if self.sessions:
            last_session = self.sessions.pop()
            device_id = last_session.device_id

            # Remove from dashboard
            last_session.remove()

            # Remove detail tab
            if device_id in self.detail_tabs:
                detail_tab = self.detail_tabs[device_id]
                detail_tab.remove()
                del self.detail_tabs[device_id]

            self._update_dashboard()

    def action_focus_tab_1(self) -> None:
        """Focus dashboard tab."""
        tabbed_content = self.query_one(TabbedContent)
        tabbed_content.active = "dashboard-tab"

    def action_focus_tab_n(self, event) -> None:
        """Focus session tab by number."""
        try:
            tab_number = int(event.character) - 1  # Convert to 0-based
            if 0 <= tab_number < len(self.sessions):
                device_id = self.sessions[tab_number].device_id
                tab_id = f"detail-{device_id}"
                tabbed_content = self.query_one(TabbedContent)
                tabbed_content.active = tab_id
        except:
            pass

    def action_next_tab(self) -> None:
        """Switch to next tab."""
        tabbed_content = self.query_one(TabbedContent)
        current = tabbed_content.active
        all_tabs = ["dashboard-tab"] + [f"detail-{s.device_id}" for s in self.sessions]

        if current in all_tabs:
            current_index = all_tabs.index(current)
            next_index = (current_index + 1) % len(all_tabs)
            tabbed_content.active = all_tabs[next_index]

    def action_previous_tab(self) -> None:
        """Switch to previous tab."""
        tabbed_content = self.query_one(TabbedContent)
        current = tabbed_content.active
        all_tabs = ["dashboard-tab"] + [f"detail-{s.device_id}" for s in self.sessions]

        if current in all_tabs:
            current_index = all_tabs.index(current)
            prev_index = (current_index - 1) % len(all_tabs)
            tabbed_content.active = all_tabs[prev_index]

    def action_simulate_job(self) -> None:
        """Simulate a job on first idle device."""
        idle_sessions = [s for s in self.sessions if s.state == "NEW"]
        if idle_sessions:
            session = idle_sessions[0]
            session.job_name = f"simulated-{int(time.time())}.svg"
            asyncio.create_task(self._simulate_session_workflow(session))

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    async def _simulate_session_workflow(self, session: SessionWidget) -> None:
        """Simulate complete session workflow."""
        device_id = session.device_id
        detail_tab = self.detail_tabs.get(device_id)

        workflow_steps = [
            ("QUEUED", 1.0),
            ("ANALYZED", 2.0),
            ("OPTIMIZED", 2.0),
            ("READY", 1.0),
            ("ARMED", 1.0),
        ]

        for state, duration in workflow_steps:
            session.state = state
            if detail_tab:
                detail_tab.update_session_data(state=state, job_name=session.job_name)
                detail_tab.add_log_entry(f"State changed to: {state}")
            self._update_dashboard()
            await asyncio.sleep(duration)

        # Start plotting
        session.state = "PLOTTING"
        if detail_tab:
            detail_tab.update_session_data(state="PLOTTING")
            detail_tab.add_log_entry("Started plotting")
        self._update_dashboard()

        # Simulate plotting progress
        for progress in range(20, 101, 20):
            session.progress = progress
            if detail_tab:
                detail_tab.update_session_data(progress=progress)
                detail_tab.add_log_entry(f"Progress: {progress}%")
            await asyncio.sleep(2.0)

        # Complete
        session.state = "COMPLETED"
        if detail_tab:
            detail_tab.update_session_data(state="COMPLETED")
            detail_tab.add_log_entry("Plotting completed successfully")
        self._update_dashboard()

    def _start_simulation(self) -> None:
        """Start automatic simulation."""

        def repeat_simulation():
            self.action_simulate_job()

        # Don't await, let it run in background
        self.set_timer(10.0, repeat_simulation)

        self.set_timer(10.0, repeat_simulation)

    def on_session_details_requested(self, message: SessionDetailsRequested) -> None:
        """Handle request to open session details."""
        tab_id = f"detail-{message.device_id}"
        tabbed_content = self.query_one(TabbedContent)
        tabbed_content.active = tab_id

    def on_session_control_requested(self, message: SessionControlRequested) -> None:
        """Handle control request from detail view."""
        device_id = message.device_id
        action = message.action

        # Find the session widget
        session = next((s for s in self.sessions if s.device_id == device_id), None)
        detail_tab = self.detail_tabs.get(device_id)

        if not session:
            return

        if action == "queue" and session.state in [
            "NEW",
            "COMPLETED",
            "ABORTED",
            "FAILED",
        ]:
            session.state = "QUEUED"
            if detail_tab:
                detail_tab.update_session_data(state="QUEUED")
                detail_tab.add_log_entry("Job queued")

        elif action == "start" and session.state in ["READY", "ARMED", "PAUSED"]:
            session.state = "PLOTTING"
            if detail_tab:
                detail_tab.update_session_data(state="PLOTTING")
                detail_tab.add_log_entry("Started plotting")

        elif action == "pause" and session.state == "PLOTTING":
            session.state = "PAUSED"
            if detail_tab:
                detail_tab.update_session_data(state="PAUSED")
                detail_tab.add_log_entry("Plotting paused")

        elif action == "abort" and session.state in [
            "QUEUED",
            "ARMED",
            "PLOTTING",
            "PAUSED",
        ]:
            session.state = "ABORTED"
            if detail_tab:
                detail_tab.update_session_data(state="ABORTED")
                detail_tab.add_log_entry("Plotting aborted")

        elif action == "reset" and session.state in COMPLETED_STATES:
            session.state = "NEW"
            session.job_name = ""
            session.progress = 0.0
            if detail_tab:
                detail_tab.update_session_data(state="NEW", job_name="", progress=0.0)
                detail_tab.add_log_entry("Session reset")

        self._update_dashboard()


def main():
    """Run ploTTY tabbed TUI demo."""
    print("Starting ploTTY Session Manager TUI with Tabbed Interface")
    print("=" * 60)
    print("Features:")
    print("- 📊 Dashboard: Overview of all sessions")
    print("- 📋 Individual Tabs: Detailed view for each device")
    print("- 🔄 Real-time Updates: Live state changes")
    print("- 📝 Session Logs: Detailed activity tracking")
    print("=" * 60)
    print("Keyboard shortcuts:")
    print("- '1': Dashboard tab")
    print("- '2-9': Session detail tabs")
    print("- 'Ctrl+Tab': Next tab")
    print("- 'Ctrl+Shift+Tab': Previous tab")
    print("- 'a': Add new session")
    print("- 'space': Simulate new job")
    print("- 'd': Toggle dark mode")
    print("- 'q': Quit")
    print("=" * 60)
    print("The demo will automatically simulate jobs every 10 seconds.")
    print("=" * 60)

    app = PlottyTabbedTUIApp()
    app.run()


if __name__ == "__main__":
    main()
