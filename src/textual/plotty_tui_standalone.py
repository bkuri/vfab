#!/usr/bin/env python3
"""
ploTTY TUI Standalone Version

Simplified TUI with embedded backend classes for testing.
Includes device health monitoring and layer progress visualization.
"""

import asyncio
import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll, Grid
from textual.reactive import reactive
from textual.widgets import (
    Button,
    Label,
    ProgressBar,
    Static,
    Header,
    Footer,
    TabbedContent,
    TabPane,
    RichLog,
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


@dataclass
class Device:
    """Simple device model."""

    id: str
    name: str
    port: str
    is_active: bool = False
    current_job_id: Optional[str] = None


@dataclass
class Job:
    """Simple job model."""

    id: str
    name: str
    state: str
    device_id: str
    progress: float = 0.0
    current_layer: int = 0
    total_layers: int = 0
    eta_seconds: int = 0


class LayerProgressBar(Vertical):
    """Enhanced progress bar with layer visualization."""

    def __init__(self, total_layers: int = 1, **kwargs):
        super().__init__(**kwargs)
        self.total_layers = total_layers
        self.current_layer = 0

    def compose(self) -> ComposeResult:
        yield Label("Layer Progress", classes="progress-title")
        yield ProgressBar(total=100, show_eta=False, id="overall-progress")

        with Vertical(id="layers-container"):
            for i in range(self.total_layers):
                yield ProgressBar(
                    total=100, show_eta=False, id=f"layer-{i}", classes="layer-bar"
                )

    def update_progress(self, current_layer: int, overall_progress: float) -> None:
        """Update layer and overall progress."""
        self.current_layer = current_layer

        # Update overall progress
        try:
            overall_bar = self.query_one("#overall-progress", ProgressBar)
            overall_bar.progress = overall_progress
        except:
            pass

        # Update layer progress
        for i in range(self.total_layers):
            try:
                layer_bar = self.query_one(f"#layer-{i}", ProgressBar)
                if i < current_layer:
                    layer_bar.progress = 100.0
                elif i == current_layer:
                    # Calculate current layer progress
                    layer_progress = (
                        overall_progress % (100 / self.total_layers)
                    ) * self.total_layers
                    layer_bar.progress = min(layer_progress, 100.0)
                else:
                    layer_bar.progress = 0.0
            except:
                pass


class DeviceHealthWidget(Vertical):
    """Widget for displaying device health information."""

    def __init__(self, device_id: str, **kwargs):
        super().__init__(**kwargs)
        self.device_id = device_id
        self.health_data = {}

    def compose(self) -> ComposeResult:
        yield Label("Device Health", classes="health-title")

        with Grid():
            yield Label("Health Score:", classes="health-label")
            yield ProgressBar(total=100, id="health-gauge", classes="health-gauge")

            yield Label("Temperature:", classes="health-label")
            yield Label("--°C", id="temperature", classes="health-value")

            yield Label("Motor Hours:", classes="health-label")
            yield Label("--", id="motor-hours", classes="health-value")

            yield Label("Error Count:", classes="health-label")
            yield Label("--", id="error-count", classes="health-value")

    def update_health(self, health_data: Dict[str, Any]) -> None:
        """Update health display."""
        self.health_data = health_data

        try:
            # Update health gauge
            health_gauge = self.query_one("#health-gauge", ProgressBar)
            health_score = health_data.get("health_score", 100.0)
            health_gauge.progress = health_score

            # Update temperature
            temp_label = self.query_one("#temperature", Label)
            temperature = health_data.get("temperature", 0.0)
            temp_label.update(f"{temperature:.1f}°C")

            # Update motor hours
            motor_label = self.query_one("#motor-hours", Label)
            motor_hours = health_data.get("motor_hours", 0.0)
            motor_label.update(f"{motor_hours:.1f}")

            # Update error count
            error_label = self.query_one("#error-count", Label)
            error_count = health_data.get("error_count", 0)
            error_label.update(str(error_count))

        except:
            pass


class SessionWidget(Vertical):
    """Enhanced session widget with mock backend integration."""

    def __init__(self, device: Device, **kwargs):
        super().__init__(**kwargs)
        self.device = device
        self.current_job: Optional[Job] = None

    # Reactive properties
    state = reactive("NEW")
    job_name = reactive("")
    progress = reactive(0.0)
    current_layer = reactive(0)
    total_layers = reactive(0)
    eta_seconds = reactive(0)

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        with Horizontal(classes="session-header"):
            yield Label(f"Device: {self.device.name}", classes="device-name")
            yield Label(self._get_state_display(), classes="state-label")
            yield Label(f"Port: {self.device.port}", classes="port-label")

        with Horizontal(classes="session-info"):
            yield Label(f"Job: {self.job_name or 'None'}", classes="job-name")
            yield ProgressBar(total=100, show_eta=True, classes="progress-bar")

        with Horizontal(classes="session-details"):
            yield Label(
                f"Layer: {self.current_layer}/{self.total_layers}", classes="layer-info"
            )
            yield Label(f"ETA: {self._format_eta()}", classes="eta-info")

        # Layer progress visualization
        yield LayerProgressBar(
            total_layers=self.total_layers or 1, classes="layer-progress"
        )

        with Horizontal(classes="session-controls"):
            yield Button("Queue", id="queue", variant="primary")
            yield Button("Start", id="start", variant="success")
            yield Button("Pause", id="pause", variant="warning")
            yield Button("Abort", id="abort", variant="error")
            yield Button("Reset", id="reset")

    def on_mount(self) -> None:
        """Initialize widget when mounted."""
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
        return state_colors.get(self.state, f"❓ {self.state}")

    def _format_eta(self) -> str:
        """Format ETA display."""
        if self.eta_seconds <= 0:
            return "--:--:--"

        minutes, seconds = divmod(self.eta_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f}"

    def _update_button_visibility(self) -> None:
        """Update button visibility based on current state."""
        buttons = {
            "queue": self.state in ["NEW", "COMPLETED", "ABORTED", "FAILED"],
            "start": self.state in ["READY", "ARMED", "PAUSED"],
            "pause": self.state == "PLOTTING",
            "abort": self.state in ["QUEUED", "ARMED", "PLOTTING", "PAUSED"],
            "reset": self.state in COMPLETED_STATES,
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
        self.add_class(f"state-{self.state.lower()}")

        # Add generic status classes
        if self.state in ACTIVE_STATES:
            self.add_class("active")
        elif self.state in COMPLETED_STATES:
            self.add_class("completed")
        else:
            self.add_class("idle")

    def update_from_job(self, job: Job) -> None:
        """Update widget from job data."""
        self.current_job = job
        self.job_name = job.name
        self.state = job.state
        self.progress = job.progress
        self.current_layer = job.current_layer
        self.total_layers = job.total_layers
        self.eta_seconds = job.eta_seconds

        # Update layer progress
        try:
            layer_progress = self.query_one(LayerProgressBar)
            layer_progress.update_progress(job.current_layer, job.progress)
        except:
            pass

    def watch_state(self, state: str) -> None:
        """Called when the state attribute changes."""
        self._update_button_visibility()
        self._update_classes()

    def watch_job_name(self, job_name: str) -> None:
        """Called when job name changes."""
        try:
            job_label = self.query_one(".job-name", Label)
            job_label.update(f"Job: {job_name or 'None'}")
        except:
            pass

    def watch_progress(self, progress: float) -> None:
        """Called when progress changes."""
        try:
            progress_bar = self.query_one(".progress-bar", ProgressBar)
            progress_bar.progress = progress
        except:
            pass

    def watch_current_layer(self, current_layer: int) -> None:
        """Called when current layer changes."""
        try:
            layer_label = self.query_one(".layer-info", Label)
            layer_label.update(f"Layer: {current_layer}/{self.total_layers}")
        except:
            pass

    def watch_eta_seconds(self, eta_seconds: int) -> None:
        """Called when ETA changes."""
        try:
            eta_label = self.query_one(".eta-info", Label)
            eta_label.update(f"ETA: {self._format_eta()}")
        except:
            pass

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses with mock backend integration."""
        button_id = event.button.id

        if button_id == "start" and self.state in ["READY", "ARMED", "PAUSED"]:
            self.state = "PLOTTING"
            asyncio.create_task(self._simulate_progress())

        elif button_id == "pause" and self.state == "PLOTTING":
            self.state = "PAUSED"

        elif button_id == "abort" and self.state in [
            "QUEUED",
            "ARMED",
            "PLOTTING",
            "PAUSED",
        ]:
            self.state = "ABORTED"

        elif button_id == "queue" and self.state in [
            "NEW",
            "COMPLETED",
            "ABORTED",
            "FAILED",
        ]:
            self.state = "QUEUED"
            # Simulate job processing
            await asyncio.sleep(1)
            self.state = "ANALYZED"
            await asyncio.sleep(1)
            self.state = "OPTIMIZED"
            await asyncio.sleep(1)
            self.state = "READY"
            await asyncio.sleep(1)
            self.state = "ARMED"

        elif button_id == "reset" and self.state in COMPLETED_STATES:
            self.state = "NEW"
            self.progress = 0.0
            self.current_layer = 0
            self.total_layers = 0
            self.eta_seconds = 0
            self.job_name = ""

    async def _simulate_progress(self) -> None:
        """Simulate plotting progress."""
        if not self.current_job:
            # Create a mock job
            self.current_job = Job(
                id=f"job-{int(time.time())}",
                name="test-job.svg",
                state="PLOTTING",
                device_id=self.device.id,
                total_layers=5,
            )
            self.total_layers = 5
            self.job_name = self.current_job.name

        # Simulate layer-by-layer progress
        for layer in range(self.total_layers):
            if self.state != "PLOTTING":
                break

            self.current_layer = layer + 1

            # Simulate progress within current layer
            layer_progress_steps = 20
            for step in range(layer_progress_steps):
                if self.state != "PLOTTING":
                    break

                overall_progress = (
                    ((layer * layer_progress_steps) + step)
                    / (self.total_layers * layer_progress_steps)
                    * 100
                )
                self.progress = overall_progress

                # Update ETA (decreasing)
                remaining_steps = (self.total_layers * layer_progress_steps) - (
                    (layer * layer_progress_steps) + step
                )
                self.eta_seconds = max(0, remaining_steps * 0.5)  # 0.5 seconds per step

                await asyncio.sleep(0.1)

            # Brief pause between layers
            if self.state == "PLOTTING":
                await asyncio.sleep(0.5)

        # Complete the job
        if self.state == "PLOTTING":
            self.state = "COMPLETED"
            self.progress = 100.0


class DashboardTab(TabPane):
    """Enhanced dashboard with mock backend integration."""

    def __init__(self, **kwargs):
        # Remove title from kwargs if present to avoid conflict
        kwargs.pop("title", None)
        super().__init__(title="📊 Dashboard", **kwargs)
        self.session_widgets: Dict[str, SessionWidget] = {}

    def compose(self) -> ComposeResult:
        """Create dashboard content."""
        yield Label("ploTTY Session Manager", classes="dashboard-title")

        with Horizontal(classes="dashboard-stats"):
            yield Static("Active: 0", id="active-count", classes="stat-box")
            yield Static("Idle: 0", id="idle-count", classes="stat-box")
            yield Static("Total: 0", id="total-count", classes="stat-box")
            yield Static("Jobs: 0", id="jobs-count", classes="stat-box")

        with Horizontal(classes="main-content"):
            # Sessions panel
            with Vertical(classes="sessions-panel"):
                yield Label("Active Sessions", classes="panel-title")
                yield VerticalScroll(id="sessions-container", classes="sessions-scroll")

            # Health and logs panel
            with Vertical(classes="info-panel"):
                yield Label("System Information", classes="panel-title")
                yield RichLog(id="system-log", classes="system-log")
                yield DeviceHealthWidget("system", classes="health-widget")

    def on_mount(self) -> None:
        """Initialize dashboard."""
        asyncio.create_task(self._setup_mock_devices())
        self._start_health_monitoring()

    async def _setup_mock_devices(self) -> None:
        """Setup mock devices."""
        devices = [
            Device("axidraw-1", "Axidraw #1", "/dev/ttyUSB0"),
            Device("axidraw-2", "Axidraw #2", "/dev/ttyUSB1"),
            Device("axidraw-3", "Axidraw #3", "/dev/ttyUSB2"),
        ]

        for device in devices:
            await self.create_session_widget(device)

    def _start_health_monitoring(self) -> None:
        """Start periodic health monitoring."""

        def update_health():
            task = asyncio.create_task(self._update_system_health())
            return task

        self.health_timer = self.set_interval(30.0, update_health)

    async def _update_system_health(self) -> None:
        """Update system health information."""
        # Simulate health data
        health_data = {
            "health_score": 85.0 + (time.time() % 15),
            "temperature": 35.0 + (time.time() % 10),
            "motor_hours": 120.5 + (time.time() % 5),
            "error_count": 0,
        }

        try:
            health_widget = self.query_one(DeviceHealthWidget)
            health_widget.update_health(health_data)
        except:
            pass

    def _log_message(self, message: str) -> None:
        """Add message to system log."""
        try:
            log = self.query_one("#system-log", RichLog)
            timestamp = time.strftime("%H:%M:%S")
            log.write(f"[{timestamp}] {message}")
        except:
            pass

    def update_stats(self, devices: List[Device]) -> None:
        """Update dashboard statistics."""
        active_count = sum(1 for d in devices if d.is_active)
        idle_count = len(devices) - active_count
        total_count = len(devices)

        try:
            active_label = self.query_one("#active-count", Static)
            active_label.update(f"Active: {active_count}")

            idle_label = self.query_one("#idle-count", Static)
            idle_label.update(f"Idle: {idle_count}")

            total_label = self.query_one("#total-count", Static)
            total_label.update(f"Total: {total_count}")

            jobs_label = self.query_one("#jobs-count", Static)
            jobs_label.update(f"Jobs: {len(self.session_widgets)}")
        except:
            pass

    async def create_session_widget(self, device: Device) -> None:
        """Create a session widget for a device."""
        if device.id in self.session_widgets:
            return

        session_widget = SessionWidget(
            device=device,
            id=f"session-{device.id}",
        )

        # Add to sessions container
        sessions_container = self.query_one("#sessions-container")
        await sessions_container.mount(session_widget)

        self.session_widgets[device.id] = session_widget
        self.update_stats([device])


class PloTTYTUIApp(App):
    """ploTTY TUI with mock backend integration."""

    CSS = """
    /* Dashboard Styles */
    .dashboard-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        height: 3;
        margin: 1 0;
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

    .main-content {
        height: 1fr;
    }

    .sessions-panel {
        width: 3fr;
        height: 1fr;
        margin: 0 1 0 0;
    }

    .info-panel {
        width: 2fr;
        height: 1fr;
    }

    .panel-title {
        text-style: bold;
        color: $accent;
        height: 2;
        margin: 0 0 1 0;
    }

    .sessions-scroll {
        height: 1fr;
        border: solid $primary;
        background: $surface;
    }

    .system-log {
        height: 15;
        background: $panel;
        border: solid $surface;
        margin: 0 0 1 0;
    }

    .health-widget {
        height: 1fr;
        background: $surface;
        border: solid $panel;
    }

    /* Session Widget Styles */
    SessionWidget {
        background: $boost;
        height: auto;
        min-height: 15;
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
        text-align: center;
        color: $foreground-muted;
    }

    .port-label {
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

    .session-details {
        height: 2;
        margin-bottom: 1;
    }

    .layer-info, .eta-info {
        width: 1fr;
        color: $foreground-muted;
    }

    .layer-progress {
        height: 8;
        margin-bottom: 1;
        background: $surface;
        border: solid $panel;
        padding: 1;
    }

    .progress-title {
        text-style: bold;
        color: $accent;
        height: 2;
        margin-bottom: 1;
    }

    .layer-bar {
        height: 2;
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
        border: solid $success;
    }

    SessionWidget.state-paused {
        background: $warning;
        color: $text;
        border: solid $warning;
    }

    SessionWidget.state-completed {
        background: $success-muted;
    }

    SessionWidget.state-failed, SessionWidget.state-aborted {
        background: $error;
        color: $text;
        border: solid $error;
    }

    /* Health Widget Styles */
    .health-title {
        text-style: bold;
        color: $accent;
        height: 2;
        margin-bottom: 1;
    }

    .health-label {
        color: $text;
        height: 2;
    }

    .health-value {
        color: $foreground-muted;
        height: 2;
        text-align: right;
    }

    .health-gauge {
        height: 3;
    }

    /* TabbedContent adjustments */
    TabbedContent {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("d", "toggle_dark", "Toggle dark mode"),
        Binding("q", "quit", "Quit"),
        Binding("space", "add_job", "Add Job"),
        Binding("f5", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        """Create the main application layout."""
        yield Header()

        with TabbedContent(id="main-tabs"):
            yield DashboardTab(id="dashboard-tab")

        yield Footer()

    async def action_add_job(self) -> None:
        """Add a new job."""
        try:
            dashboard = self.query_one("#dashboard-tab", DashboardTab)
            if dashboard.session_widgets:
                # Get first session widget
                session_widget = next(iter(dashboard.session_widgets.values()))
                # Simulate adding a job
                session_widget.job_name = f"manual-job-{int(time.time())}.svg"
                session_widget.state = "QUEUED"
                dashboard._log_message(f"Added job to {session_widget.device.name}")
            else:
                dashboard._log_message("No devices available")
        except:
            pass

    async def action_refresh(self) -> None:
        """Refresh data."""
        try:
            dashboard = self.query_one("#dashboard-tab", DashboardTab)
            dashboard._log_message("Data refreshed")
        except:
            pass


async def main():
    """Run the ploTTY TUI."""
    print("Starting ploTTY TUI (Standalone Version)")
    print("=" * 60)
    print("Features:")
    print("- 📊 Device health monitoring")
    print("- 📈 Layer-by-layer progress visualization")
    print("- 📝 System logging")
    print("- 🎛️ Full FSM state management")
    print("- 🔄 Mock backend simulation")
    print("=" * 60)
    print("Keyboard shortcuts:")
    print("- 'space': Add new job")
    print("- 'r': Refresh data")
    print("- 'd': Toggle dark mode")
    print("- 'q': Quit")
    print("=" * 60)

    app = PloTTYTUIApp()
    await app.run_async()


if __name__ == "__main__":
    asyncio.run(main())
