"""
Example integration of ploTTY TUI with backend systems.

This file demonstrates how to connect the session manager TUI with:
1. ploTTY FSM (Finite State Machine)
2. Database models
3. Device drivers
4. Job queue management

Run this as a standalone example to see the integration in action.
"""

import asyncio
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Import our TUI components
from session_manager_simple import SessionManagerApp, FSM_STATES, ACTIVE_STATES


class DeviceType(Enum):
    AXIDRAW = "axidraw"
    HPGL = "hpgl"
    CUSTOM = "custom"


@dataclass
class Device:
    """Device model matching ploTTY database schema."""

    id: str
    name: str
    kind: DeviceType
    port: str
    firmware: str
    is_active: bool = False
    current_job_id: Optional[str] = None


@dataclass
class Job:
    """Job model matching ploTTY database schema."""

    id: str
    name: str
    src_path: str
    opt_path: Optional[str]
    state: str
    device_id: str
    progress: float = 0.0
    current_layer: int = 0
    total_layers: int = 0
    eta_seconds: int = 0


class MockPloTTYBackend:
    """Mock backend that simulates ploTTY functionality."""

    def __init__(self):
        self.devices: Dict[str, Device] = {}
        self.jobs: Dict[str, Job] = {}
        self.tui_app: Optional[SessionManagerApp] = None
        self._setup_mock_devices()
        self._simulation_running = False

    def _setup_mock_devices(self):
        """Setup mock devices for demonstration."""
        devices = [
            Device(
                "axidraw-1", "Axidraw #1", DeviceType.AXIDRAW, "/dev/ttyUSB0", "v2.5.3"
            ),
            Device(
                "axidraw-2", "Axidraw #2", DeviceType.AXIDRAW, "/dev/ttyUSB1", "v2.5.3"
            ),
            Device(
                "axidraw-3", "Axidraw #3", DeviceType.AXIDRAW, "/dev/ttyUSB2", "v2.5.3"
            ),
        ]

        for device in devices:
            self.devices[device.id] = device

    def set_tui_app(self, app: SessionManagerApp):
        """Connect the TUI application to the backend."""
        self.tui_app = app

    def add_job(self, job_data: Dict[str, Any]) -> str:
        """Add a new job to the system."""
        job_id = f"job-{int(time.time())}"
        job = Job(
            id=job_id,
            name=job_data.get("name", "unknown.svg"),
            src_path=job_data.get("src_path", ""),
            opt_path=None,
            state="NEW",
            device_id=job_data.get("device_id", ""),
            total_layers=job_data.get("total_layers", 1),
        )

        self.jobs[job_id] = job

        # Update TUI if connected
        if self.tui_app:
            self.tui_app.add_job_to_queue(
                {"device_id": job.device_id, "job_name": job.name}
            )

        return job_id

    def update_job_state(self, job_id: str, new_state: str, **kwargs):
        """Update job state and notify TUI."""
        if job_id not in self.jobs:
            return

        job = self.jobs[job_id]
        old_state = job.state
        job.state = new_state

        # Update additional properties
        for key, value in kwargs.items():
            if hasattr(job, key):
                setattr(job, key, value)

        # Update device status
        device = self.devices.get(job.device_id)
        if device:
            if new_state in ACTIVE_STATES:
                device.is_active = True
                device.current_job_id = job_id
            else:
                device.is_active = False
                device.current_job_id = None

        # Notify TUI
        if self.tui_app:
            self.tui_app.update_session_from_backend(
                device_id=job.device_id,
                state=new_state,
                job_name=job.name,
                progress=job.progress,
                current_layer=str(job.current_layer),
                total_layers=job.total_layers,
                eta_seconds=job.eta_seconds,
            )

    async def simulate_job_execution(self, job_id: str):
        """Simulate the complete job execution lifecycle."""
        if job_id not in self.jobs:
            return

        job = self.jobs[job_id]

        # Simulate ploTTY FSM transitions
        states = [
            ("QUEUED", 1.0),
            ("ANALYZED", 2.0),
            ("OPTIMIZED", 3.0),
            ("READY", 1.0),
            ("ARMED", 1.0),
            ("PLOTTING", 10.0),  # Longer time for plotting
        ]

        for state, duration in states:
            self.update_job_state(job_id, state)
            await asyncio.sleep(duration)

            # Update progress during plotting
            if state == "PLOTTING":
                for i in range(1, job.total_layers + 1):
                    progress = (i / job.total_layers) * 100
                    self.update_job_state(
                        job_id,
                        "PLOTTING",
                        progress=progress,
                        current_layer=i,
                        eta_seconds=int((job.total_layers - i) * 2),
                    )
                    await asyncio.sleep(2.0)

                # Final completion
                self.update_job_state(job_id, "COMPLETED", progress=100.0)

    async def start_simulation(self):
        """Start the backend simulation."""
        if self._simulation_running:
            return

        self._simulation_running = True

        # Add some initial jobs
        jobs_to_add = [
            {"name": "mandala.svg", "device_id": "axidraw-1", "total_layers": 3},
            {
                "name": "geometric-pattern.svg",
                "device_id": "axidraw-3",
                "total_layers": 5,
            },
        ]

        for job_data in jobs_to_add:
            job_id = self.add_job(job_data)
            # Start simulation after a short delay
            asyncio.create_task(asyncio.sleep(2.0))
            asyncio.create_task(self.simulate_job_execution(job_id))

        # Periodically add new jobs
        while self._simulation_running:
            await asyncio.sleep(15.0)

            # Find an idle device
            idle_devices = [d for d in self.devices.values() if not d.is_active]
            if idle_devices:
                device = idle_devices[0]
                job_data = {
                    "name": f"auto-job-{int(time.time())}.svg",
                    "device_id": device.id,
                    "total_layers": 2,
                }
                job_id = self.add_job(job_data)
                asyncio.create_task(self.simulate_job_execution(job_id))

    def stop_simulation(self):
        """Stop the backend simulation."""
        self._simulation_running = False


class IntegratedSessionManager(SessionManagerApp):
    """Extended session manager with backend integration."""

    def __init__(self, backend: MockPloTTYBackend):
        super().__init__()
        self.backend = backend
        self.backend.set_tui_app(self)

    def on_mount(self) -> None:
        """Initialize the application with backend data."""
        super().on_mount()

        # Start backend simulation
        asyncio.create_task(self.backend.start_simulation())

    def action_add_session(self) -> None:
        """Override to add session with backend device info."""
        # Find next available device ID
        existing_ids = [s.device_id for s in self.sessions]
        all_device_ids = list(self.backend.devices.keys())

        for device_id in all_device_ids:
            if device_id not in existing_ids:
                device = self.backend.devices[device_id]
                self._create_session(device.name, device_id)
                self._update_device_summary()
                return

        # If all devices exist, create a new one
        super().action_add_session()

    def on_button_pressed(self, event) -> None:
        """Handle button presses with backend integration."""
        # Let parent handle first
        super().on_button_pressed(event)

        # Additional backend logic could go here
        # For example, sending commands to actual ploTTY backend


async def main():
    """Run the integrated session manager."""
    # Create backend
    backend = MockPloTTYBackend()

    # Create and run TUI
    app = IntegratedSessionManager(backend)

    try:
        await app.run_async()
    finally:
        backend.stop_simulation()


if __name__ == "__main__":
    print("Starting ploTTY Session Manager with Backend Integration")
    print("=" * 60)
    print("This demo shows:")
    print("- Multiple device session management")
    print(
        "- FSM state transitions (NEW → QUEUED → ANALYZED → OPTIMIZED → READY → ARMED → PLOTTING → COMPLETED)"
    )
    print("- Real-time progress updates")
    print("- Job queue management")
    print("- Device status tracking")
    print("\nKeyboard shortcuts:")
    print("- 'a': Add new session")
    print("- 'r': Remove last session")
    print("- 's': Toggle queue visibility")
    print("- 'd': Toggle dark mode")
    print("- 'q': Quit")
    print("=" * 60)

    asyncio.run(main())
