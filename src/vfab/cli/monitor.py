"""
CLI monitor command for vfab real-time monitoring.

This module provides a command-line interface for connecting to the
vfab WebSocket server and displaying real-time updates.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import List

import typer
import websockets
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text


class WebSocketMonitor:
    """Real-time WebSocket monitor for vfab."""

    def __init__(self, host: str, port: int, channels: List[str]):
        self.host = host
        self.port = port
        self.channels = channels
        self.console = Console()
        self.live = None
        self.jobs_data = {}
        self.devices_data = {}
        self.system_alerts = []
        self.connection_status = "Disconnected"

    def create_display(self) -> Layout:
        """Create the main display layout."""
        layout = Layout()

        # Split into sections
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3),
        )

        layout["main"].split_row(
            Layout(name="jobs", ratio=2),
            Layout(name="devices", ratio=1),
            Layout(name="alerts", ratio=1),
        )

        return layout

    def create_header(self) -> Panel:
        """Create header panel."""
        header_text = Text()
        header_text.append("vfab Monitor", style="bold blue")
        header_text.append(f" | {self.host}:{self.port}", style="dim")
        header_text.append(
            f" | {self.connection_status}",
            style="green" if self.connection_status == "Connected" else "red",
        )

        return Panel(header_text, style="bold")

    def create_jobs_table(self) -> Table:
        """Create jobs monitoring table."""
        table = Table(title="Jobs", show_header=True, header_style="bold blue")
        table.add_column("Job ID", style="cyan")
        table.add_column("State", style="magenta")
        table.add_column("Progress", style="green")
        table.add_column("ETA", style="yellow")

        for job_id, data in self.jobs_data.items():
            progress = f"{data.get('progress', 0):.1f}%"
            eta = data.get("eta", "N/A")
            table.add_row(job_id, data.get("state", "Unknown"), progress, eta)

        if not self.jobs_data:
            table.add_row("No active jobs", "", "", "")

        return table

    def create_devices_table(self) -> Table:
        """Create devices monitoring table."""
        table = Table(title="Devices", show_header=True, header_style="bold blue")
        table.add_column("Device", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Last Seen", style="green")

        for device_id, data in self.devices_data.items():
            status = data.get("status", "Unknown")
            last_seen = data.get("last_seen", "Never")
            table.add_row(device_id, status, last_seen)

        if not self.devices_data:
            table.add_row("No devices", "", "")

        return table

    def create_alerts_panel(self) -> Panel:
        """Create system alerts panel."""
        if not self.system_alerts:
            alerts_text = "No system alerts"
        else:
            alerts_text = "\\n".join(
                f"• {alert.get('title', 'Alert')}: {alert.get('message', '')}"
                for alert in self.system_alerts[-5:]  # Show last 5 alerts
            )

        return Panel(alerts_text, title="System Alerts", style="yellow")

    def create_footer(self) -> Panel:
        """Create footer panel."""
        footer_text = f"Channels: {', '.join(self.channels)} | Press Ctrl+C to exit"
        return Panel(footer_text, style="dim")

    def update_display(self) -> Layout:
        """Update the complete display."""
        layout = self.create_display()

        layout["header"].update(self.create_header())
        layout["jobs"].update(self.create_jobs_table())
        layout["devices"].update(self.create_devices_table())
        layout["alerts"].update(self.create_alerts_panel())
        layout["footer"].update(self.create_footer())

        return layout

    async def handle_message(self, message_data: dict) -> None:
        """Handle incoming WebSocket message."""
        message_type = message_data.get("type")
        timestamp = message_data.get("timestamp", datetime.now().isoformat())

        if message_type == "job_state_change":
            job_id = message_data.get("job_id", "unknown")
            self.jobs_data[job_id] = {
                "state": message_data.get("to_state", "Unknown"),
                "progress": 0.0,
                "eta": "N/A",
                "updated": timestamp,
            }

        elif message_type == "job_progress":
            job_id = message_data.get("job_id", "unknown")
            if job_id in self.jobs_data:
                self.jobs_data[job_id].update(
                    {
                        "progress": message_data.get("progress_percentage", 0.0),
                        "eta": f"{message_data.get('eta_seconds', 0)}s",
                        "updated": timestamp,
                    }
                )

        elif message_type == "device_status":
            device_id = message_data.get("device_id", "unknown")
            self.devices_data[device_id] = {
                "status": message_data.get("status", "Unknown"),
                "last_seen": timestamp,
                "updated": timestamp,
            }

        elif message_type == "system_alert":
            self.system_alerts.append(
                {
                    "title": message_data.get("title", "Alert"),
                    "message": message_data.get("message", ""),
                    "severity": message_data.get("severity", "info"),
                    "timestamp": timestamp,
                }
            )
            # Keep only last 20 alerts
            self.system_alerts = self.system_alerts[-20:]

    async def connect_and_monitor(self) -> None:
        """Connect to WebSocket and start monitoring."""
        uri = f"ws://{self.host}:{self.port}/ws"

        try:
            async with websockets.connect(uri) as websocket:
                self.connection_status = "Connected"

                # Subscribe to channels
                subscribe_msg = {"type": "SUBSCRIBE", "channels": self.channels}
                await websocket.send(json.dumps(subscribe_msg))

                # Start live display
                with Live(
                    self.update_display(), refresh_per_second=1, screen=True
                ) as self.live:
                    try:
                        while True:
                            # Receive message
                            message = await websocket.recv()
                            message_data = json.loads(message)

                            # Handle message
                            await self.handle_message(message_data)

                            # Update display
                            if self.live:
                                self.live.update(self.update_display())

                    except websockets.exceptions.ConnectionClosed:
                        self.connection_status = "Disconnected"
                        return
                    except Exception as e:
                        self.console.print(f"Error receiving message: {e}", style="red")
                        return

        except Exception as e:
            self.console.print(f"Failed to connect to {uri}: {e}", style="red")
            self.connection_status = "Connection Failed"


def monitor_command(
    host: str = typer.Option("localhost", "--host", help="WebSocket server host"),
    port: int = typer.Option(8765, "--port", help="WebSocket server port"),
    channels: List[str] = typer.Option(
        ["jobs", "devices", "system"], "--channel", help="Channels to subscribe to"
    ),
) -> None:
    """Connect to vfab WebSocket server and display real-time monitoring."""

    # Validate channels
    valid_channels = ["jobs", "devices", "system", "all"]
    for channel in channels:
        if channel not in valid_channels:
            typer.echo(f"Invalid channel: {channel}", err=True)
            typer.echo(f"Valid channels: {', '.join(valid_channels)}", err=True)
            raise typer.Exit(1)

    # Create and run monitor
    monitor = WebSocketMonitor(host, port, channels)

    try:
        asyncio.run(monitor.connect_and_monitor())
    except KeyboardInterrupt:
        typer.echo("\\nMonitor stopped by user")
    except Exception as e:
        typer.echo(f"Monitor failed: {e}", err=True)
        raise typer.Exit(1)
