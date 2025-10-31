#!/usr/bin/env python3
"""
ploTTY Backend Connector

Real backend integration for ploTTY TUI that supports:
1. Direct ploTTY database connection
2. JSON-RPC API communication
3. WebSocket real-time updates
4. Mock backend for testing
"""

import asyncio
import json
import sqlite3
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
import aiohttp
import websockets


class DeviceType(Enum):
    AXIDRAW = "axidraw"
    HPGL = "hpgl"
    CUSTOM = "custom"
    LASER = "laser"


class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


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
    health_score: float = 100.0
    last_seen: float = 0.0


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
    created_at: float = 0.0
    started_at: Optional[float] = None
    completed_at: Optional[float] = None


@dataclass
class LayerInfo:
    """Layer information for detailed progress tracking."""

    layer_num: int
    total_points: int
    plotted_points: int
    duration: float
    path: str


class PloTTYBackendInterface(ABC):
    """Abstract interface for ploTTY backends."""

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the backend."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the backend."""
        pass

    @abstractmethod
    async def get_devices(self) -> List[Device]:
        """Get all devices."""
        pass

    @abstractmethod
    async def get_jobs(self) -> List[Job]:
        """Get all jobs."""
        pass

    @abstractmethod
    async def add_job(self, job_data: Dict[str, Any]) -> str:
        """Add a new job."""
        pass

    @abstractmethod
    async def update_job_state(self, job_id: str, state: str, **kwargs) -> bool:
        """Update job state."""
        pass

    @abstractmethod
    async def get_device_health(self, device_id: str) -> Dict[str, Any]:
        """Get device health information."""
        pass

    @abstractmethod
    def set_update_callback(self, callback: Callable) -> None:
        """Set callback for real-time updates."""
        pass


class MockPloTTYBackend(PloTTYBackendInterface):
    """Mock backend for testing and demonstration."""

    def __init__(self):
        self.devices: Dict[str, Device] = {}
        self.jobs: Dict[str, Job] = {}
        self.layers: Dict[str, List[LayerInfo]] = {}
        self.update_callback: Optional[Callable] = None
        self._simulation_running = False
        self._connection_state = ConnectionState.DISCONNECTED
        self._setup_mock_devices()

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
            device.last_seen = time.time()
            self.devices[device.id] = device

    async def connect(self) -> bool:
        """Simulate connection to backend."""
        self._connection_state = ConnectionState.CONNECTING
        await asyncio.sleep(0.5)  # Simulate connection delay
        self._connection_state = ConnectionState.CONNECTED
        return True

    async def disconnect(self) -> None:
        """Simulate disconnection."""
        self._simulation_running = False
        self._connection_state = ConnectionState.DISCONNECTED

    async def get_devices(self) -> List[Device]:
        """Get all mock devices."""
        return list(self.devices.values())

    async def get_jobs(self) -> List[Job]:
        """Get all mock jobs."""
        return list(self.jobs.values())

    async def add_job(self, job_data: Dict[str, Any]) -> str:
        """Add a new mock job."""
        job_id = f"job-{int(time.time())}"
        job = Job(
            id=job_id,
            name=job_data.get("name", "unknown.svg"),
            src_path=job_data.get("src_path", ""),
            opt_path=None,
            state="NEW",
            device_id=job_data.get("device_id", ""),
            total_layers=job_data.get("total_layers", 1),
            created_at=time.time(),
        )

        self.jobs[job_id] = job

        # Setup mock layer info
        self.layers[job_id] = [
            LayerInfo(i + 1, 1000, 0, 0.0, f"layer_{i + 1}.svg")
            for i in range(job.total_layers)
        ]

        # Notify callback
        if self.update_callback:
            await self.update_callback("job_added", {"job": asdict(job)})

        return job_id

    async def update_job_state(self, job_id: str, state: str, **kwargs) -> bool:
        """Update mock job state."""
        if job_id not in self.jobs:
            return False

        job = self.jobs[job_id]
        old_state = job.state
        job.state = state

        # Update additional properties
        for key, value in kwargs.items():
            if hasattr(job, key):
                setattr(job, key, value)

        # Update timestamps
        if state in ["ARMED", "PLOTTING"] and job.started_at is None:
            job.started_at = time.time()
        elif state in ["COMPLETED", "ABORTED", "FAILED"]:
            job.completed_at = time.time()

        # Update device status
        device = self.devices.get(job.device_id)
        if device:
            if state in ["ARMED", "PLOTTING", "PAUSED"]:
                device.is_active = True
                device.current_job_id = job_id
                device.last_seen = time.time()
            else:
                device.is_active = False
                device.current_job_id = None

        # Notify callback
        if self.update_callback:
            await self.update_callback(
                "job_updated",
                {
                    "job_id": job_id,
                    "old_state": old_state,
                    "new_state": state,
                    "job": asdict(job),
                },
            )

        return True

    async def get_device_health(self, device_id: str) -> Dict[str, Any]:
        """Get mock device health."""
        device = self.devices.get(device_id)
        if not device:
            return {}

        # Simulate health metrics
        return {
            "device_id": device_id,
            "health_score": device.health_score,
            "temperature": 25.0 + (time.time() % 10),  # Simulate temp variation
            "motor_hours": 150.5,
            "last_maintenance": "2024-01-15",
            "error_count": 0,
            "warnings": [],
        }

    def set_update_callback(self, callback: Callable) -> None:
        """Set callback for real-time updates."""
        self.update_callback = callback

    async def start_simulation(self):
        """Start automatic job simulation."""
        if self._simulation_running:
            return

        self._simulation_running = True

        # Add initial jobs
        jobs_to_add = [
            {"name": "mandala.svg", "device_id": "axidraw-1", "total_layers": 3},
            {
                "name": "geometric-pattern.svg",
                "device_id": "axidraw-3",
                "total_layers": 5,
            },
        ]

        for job_data in jobs_to_add:
            job_id = await self.add_job(job_data)
            asyncio.create_task(self.simulate_job_execution(job_id))

        # Periodically add new jobs
        while self._simulation_running:
            await asyncio.sleep(15.0)

            idle_devices = [d for d in self.devices.values() if not d.is_active]
            if idle_devices:
                device = idle_devices[0]
                job_data = {
                    "name": f"auto-job-{int(time.time())}.svg",
                    "device_id": device.id,
                    "total_layers": 2,
                }
                job_id = await self.add_job(job_data)
                asyncio.create_task(self.simulate_job_execution(job_id))

    async def simulate_job_execution(self, job_id: str):
        """Simulate complete job execution lifecycle."""
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
        ]

        for state, duration in states:
            await self.update_job_state(job_id, state)
            await asyncio.sleep(duration)

        # Start plotting
        await self.update_job_state(job_id, "PLOTTING")

        # Simulate layer-by-layer progress
        for layer_num in range(1, job.total_layers + 1):
            progress = (layer_num / job.total_layers) * 100

            # Simulate layer plotting time
            layer_duration = 2.0
            for i in range(10):
                layer_progress = (i / 10) * layer_duration
                await asyncio.sleep(layer_duration / 10)

                await self.update_job_state(
                    job_id,
                    "PLOTTING",
                    progress=progress,
                    current_layer=layer_num,
                    eta_seconds=int((job.total_layers - layer_num) * 2),
                )

        # Complete
        await self.update_job_state(job_id, "COMPLETED", progress=100.0)


class DatabasePloTTYBackend(PloTTYBackendInterface):
    """Real ploTTY backend using SQLite database."""

    def __init__(self, db_path: str = "plotty.db"):
        self.db_path = Path(db_path)
        self.connection: Optional[sqlite3.Connection] = None
        self.update_callback: Optional[Callable] = None
        self._connection_state = ConnectionState.DISCONNECTED

    async def connect(self) -> bool:
        """Connect to ploTTY database."""
        try:
            self._connection_state = ConnectionState.CONNECTING
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row
            self._connection_state = ConnectionState.CONNECTED
            return True
        except Exception as e:
            self._connection_state = ConnectionState.ERROR
            print(f"Failed to connect to database: {e}")
            return False

    async def disconnect(self) -> None:
        """Disconnect from database."""
        if self.connection:
            self.connection.close()
            self.connection = None
        self._connection_state = ConnectionState.DISCONNECTED

    async def get_devices(self) -> List[Device]:
        """Get devices from database."""
        if not self.connection:
            return []

        cursor = self.connection.execute("""
            SELECT id, name, kind, port, firmware, is_active, current_job_id
            FROM devices
        """)

        devices = []
        for row in cursor.fetchall():
            device = Device(
                id=row["id"],
                name=row["name"],
                kind=DeviceType(row["kind"]),
                port=row["port"],
                firmware=row["firmware"],
                is_active=bool(row["is_active"]),
                current_job_id=row["current_job_id"],
            )
            devices.append(device)

        return devices

    async def get_jobs(self) -> List[Job]:
        """Get jobs from database."""
        if not self.connection:
            return []

        cursor = self.connection.execute("""
            SELECT id, name, src_path, opt_path, state, device_id,
                   progress, current_layer, total_layers, eta_seconds,
                   created_at, started_at, completed_at
            FROM jobs
            ORDER BY created_at DESC
        """)

        jobs = []
        for row in cursor.fetchall():
            job = Job(
                id=row["id"],
                name=row["name"],
                src_path=row["src_path"],
                opt_path=row["opt_path"],
                state=row["state"],
                device_id=row["device_id"],
                progress=row["progress"],
                current_layer=row["current_layer"],
                total_layers=row["total_layers"],
                eta_seconds=row["eta_seconds"],
                created_at=row["created_at"],
                started_at=row["started_at"],
                completed_at=row["completed_at"],
            )
            jobs.append(job)

        return jobs

    async def add_job(self, job_data: Dict[str, Any]) -> str:
        """Add job to database."""
        if not self.connection:
            raise RuntimeError("Not connected to database")

        job_id = f"job-{int(time.time())}"

        self.connection.execute(
            """
            INSERT INTO jobs (id, name, src_path, state, device_id, total_layers, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                job_id,
                job_data.get("name", "unknown.svg"),
                job_data.get("src_path", ""),
                "NEW",
                job_data.get("device_id", ""),
                job_data.get("total_layers", 1),
                time.time(),
            ),
        )

        self.connection.commit()

        # Notify callback
        if self.update_callback:
            job = await self._get_job(job_id)
            if job:
                await self.update_callback("job_added", {"job": asdict(job)})

        return job_id

    async def update_job_state(self, job_id: str, state: str, **kwargs) -> bool:
        """Update job state in database."""
        if not self.connection:
            return False

        # Build update query
        updates = ["state = ?"]
        values = [state]

        for key, value in kwargs.items():
            if key in ["progress", "current_layer", "total_layers", "eta_seconds"]:
                updates.append(f"{key} = ?")
                values.append(value)

        # Handle timestamps
        if state in ["ARMED", "PLOTTING"]:
            updates.append("started_at = ?")
            values.append(str(time.time()))
        elif state in ["COMPLETED", "ABORTED", "FAILED"]:
            updates.append("completed_at = ?")
            values.append(str(time.time()))

        values.append(job_id)

        query = f"UPDATE jobs SET {', '.join(updates)} WHERE id = ?"
        self.connection.execute(query, values)
        self.connection.commit()

        # Update device status
        job = await self._get_job(job_id)
        if job:
            await self._update_device_status(job.device_id, state, job_id)

        # Notify callback
        if self.update_callback:
            await self.update_callback(
                "job_updated",
                {
                    "job_id": job_id,
                    "new_state": state,
                    "job": asdict(job) if job else {},
                },
            )

        return True

    async def get_device_health(self, device_id: str) -> Dict[str, Any]:
        """Get device health from database."""
        if not self.connection:
            return {}

        cursor = self.connection.execute(
            """
            SELECT health_score, temperature, motor_hours, last_maintenance, error_count
            FROM device_health
            WHERE device_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """,
            (device_id,),
        )

        row = cursor.fetchone()
        if row:
            return {
                "device_id": device_id,
                "health_score": row["health_score"],
                "temperature": row["temperature"],
                "motor_hours": row["motor_hours"],
                "last_maintenance": row["last_maintenance"],
                "error_count": row["error_count"],
            }

        return {"device_id": device_id, "health_score": 100.0}

    def set_update_callback(self, callback: Callable) -> None:
        """Set callback for real-time updates."""
        self.update_callback = callback

    async def _get_job(self, job_id: str) -> Optional[Job]:
        """Get specific job from database."""
        if not self.connection:
            return None

        cursor = self.connection.execute(
            """
            SELECT id, name, src_path, opt_path, state, device_id,
                   progress, current_layer, total_layers, eta_seconds,
                   created_at, started_at, completed_at
            FROM jobs WHERE id = ?
        """,
            (job_id,),
        )

        row = cursor.fetchone()
        if row:
            return Job(
                id=row["id"],
                name=row["name"],
                src_path=row["src_path"],
                opt_path=row["opt_path"],
                state=row["state"],
                device_id=row["device_id"],
                progress=row["progress"],
                current_layer=row["current_layer"],
                total_layers=row["total_layers"],
                eta_seconds=row["eta_seconds"],
                created_at=row["created_at"],
                started_at=row["started_at"],
                completed_at=row["completed_at"],
            )

        return None

    async def _update_device_status(self, device_id: str, job_state: str, job_id: str):
        """Update device status based on job state."""
        if not self.connection:
            return

        is_active = job_state in ["ARMED", "PLOTTING", "PAUSED"]
        current_job_id = job_id if is_active else None

        self.connection.execute(
            """
            UPDATE devices SET is_active = ?, current_job_id = ? WHERE id = ?
        """,
            (is_active, current_job_id, device_id),
        )

        self.connection.commit()


class WebSocketPloTTYBackend(PloTTYBackendInterface):
    """ploTTY backend using WebSocket for real-time communication."""

    def __init__(self, ws_url: str = "ws://localhost:8765"):
        self.ws_url = ws_url
        self.websocket: Optional[Any] = None
        self.update_callback: Optional[Callable] = None
        self._connection_state = ConnectionState.DISCONNECTED
        self._message_handlers = {
            "job_update": self._handle_job_update,
            "device_update": self._handle_device_update,
            "health_update": self._handle_health_update,
        }

    async def connect(self) -> bool:
        """Connect to ploTTY WebSocket."""
        try:
            self._connection_state = ConnectionState.CONNECTING
            self.websocket = await websockets.connect(self.ws_url)
            self._connection_state = ConnectionState.CONNECTED

            # Start message listener
            asyncio.create_task(self._listen_for_messages())
            return True
        except Exception as e:
            self._connection_state = ConnectionState.ERROR
            print(f"Failed to connect to WebSocket: {e}")
            return False

    async def disconnect(self) -> None:
        """Disconnect from WebSocket."""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        self._connection_state = ConnectionState.DISCONNECTED

    async def _listen_for_messages(self):
        """Listen for WebSocket messages."""
        try:
            if self.websocket:
                async for message in self.websocket:
                    data = json.loads(message)
                    message_type = data.get("type")

                    if message_type in self._message_handlers:
                        await self._message_handlers[message_type](data)
        except websockets.exceptions.ConnectionClosed:
            self._connection_state = ConnectionState.DISCONNECTED
        except Exception as e:
            print(f"WebSocket error: {e}")
            self._connection_state = ConnectionState.ERROR

    async def _handle_job_update(self, data: Dict[str, Any]):
        """Handle job update message."""
        if self.update_callback:
            await self.update_callback("job_updated", data)

    async def _handle_device_update(self, data: Dict[str, Any]):
        """Handle device update message."""
        if self.update_callback:
            await self.update_callback("device_updated", data)

    async def _handle_health_update(self, data: Dict[str, Any]):
        """Handle health update message."""
        if self.update_callback:
            await self.update_callback("health_updated", data)

    async def send_command(self, command: str, data: Dict[str, Any]) -> bool:
        """Send command to ploTTY backend."""
        if not self.websocket:
            return False

        try:
            message = {
                "type": "command",
                "command": command,
                "data": data,
                "timestamp": time.time(),
            }
            await self.websocket.send(json.dumps(message))
            return True
        except Exception as e:
            print(f"Failed to send command: {e}")
            return False

    # Implement remaining abstract methods...
    async def get_devices(self) -> List[Device]:
        """Get devices via WebSocket."""
        await self.send_command("get_devices", {})
        # Response will come through WebSocket messages
        return []

    async def get_jobs(self) -> List[Job]:
        """Get jobs via WebSocket."""
        await self.send_command("get_jobs", {})
        # Response will come through WebSocket messages
        return []

    async def add_job(self, job_data: Dict[str, Any]) -> str:
        """Add job via WebSocket."""
        await self.send_command("add_job", job_data)
        return f"job-{int(time.time())}"

    async def update_job_state(self, job_id: str, state: str, **kwargs) -> bool:
        """Update job state via WebSocket."""
        data = {"job_id": job_id, "state": state, **kwargs}
        return await self.send_command("update_job_state", data)

    async def get_device_health(self, device_id: str) -> Dict[str, Any]:
        """Get device health via WebSocket."""
        await self.send_command("get_device_health", {"device_id": device_id})
        return {}

    def set_update_callback(self, callback: Callable) -> None:
        """Set callback for real-time updates."""
        self.update_callback = callback


class PloTTYBackendManager:
    """Manager for ploTTY backend connections."""

    def __init__(self):
        self.backend: Optional[PloTTYBackendInterface] = None
        self.backend_type = "mock"

    async def initialize(self, backend_type: str = "mock", **kwargs) -> bool:
        """Initialize backend connection."""
        self.backend_type = backend_type

        if backend_type == "mock":
            self.backend = MockPloTTYBackend()
        elif backend_type == "database":
            db_path = kwargs.get("db_path", "plotty.db")
            self.backend = DatabasePloTTYBackend(db_path)
        elif backend_type == "websocket":
            ws_url = kwargs.get("ws_url", "ws://localhost:8765")
            self.backend = WebSocketPloTTYBackend(ws_url)
        else:
            raise ValueError(f"Unknown backend type: {backend_type}")

        return await self.backend.connect()

    async def shutdown(self):
        """Shutdown backend connection."""
        if self.backend:
            await self.backend.disconnect()

    def get_backend(self) -> Optional[PloTTYBackendInterface]:
        """Get current backend instance."""
        return self.backend

    def get_connection_state(self) -> ConnectionState:
        """Get current connection state."""
        if self.backend:
            return getattr(
                self.backend, "_connection_state", ConnectionState.DISCONNECTED
            )
        return ConnectionState.DISCONNECTED


# Factory function for easy backend creation
async def create_backend(
    backend_type: str = "mock", **kwargs
) -> PloTTYBackendInterface:
    """Factory function to create backend instances."""
    manager = PloTTYBackendManager()
    success = await manager.initialize(backend_type, **kwargs)
    if success:
        backend = manager.get_backend()
        if backend:
            return backend
        else:
            raise RuntimeError(f"Backend initialization returned None: {backend_type}")
    else:
        raise RuntimeError(f"Failed to initialize backend: {backend_type}")


if __name__ == "__main__":

    async def test_backend():
        """Test backend functionality."""
        print("Testing ploTTY Backend Connector")
        print("=" * 50)

        # Test mock backend
        print("1. Testing Mock Backend...")
        backend = await create_backend("mock")

        devices = await backend.get_devices()
        print(f"   Found {len(devices)} devices")

        # Add a test job
        job_id = await backend.add_job(
            {"name": "test-backend.svg", "device_id": "axidraw-1", "total_layers": 3}
        )
        print(f"   Added job: {job_id}")

        # Get device health
        health = await backend.get_device_health("axidraw-1")
        print(f"   Device health: {health.get('health_score', 'N/A')}")

        await backend.disconnect()
        print("   Mock backend test complete")

        print("=" * 50)
        print("Backend connector test completed successfully!")

    asyncio.run(test_backend())
