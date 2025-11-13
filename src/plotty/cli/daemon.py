"""
Daemon command for ploTTY WebSocket monitoring server.

This module provides the daemon command that runs ploTTY as a persistent
service with WebSocket monitoring capabilities.
"""

from __future__ import annotations

import asyncio
import signal
import sys
import logging

import typer
import uvicorn

from ..config import load_config
from ..websocket.server import WebSocketManager, create_websocket_app
from ..hooks import HookExecutor

logger = logging.getLogger(__name__)


class PlottyDaemon:
    """Main ploTTY daemon class."""

    def __init__(self, config):
        self.config = config
        self.websocket_manager = WebSocketManager(config.websocket)
        self.app = create_websocket_app(self.websocket_manager)
        self.server_task = None
        self.heartbeat_task = None
        self.shutdown_event = asyncio.Event()

        # Inject WebSocket manager into hook system
        HookExecutor.websocket_manager = self.websocket_manager

    async def start(self, host: str = None, port: int = None):
        """Start the daemon server."""
        # Override config with CLI args
        server_host = host or self.config.websocket.host
        server_port = port or self.config.websocket.port

        logger.info(f"Starting ploTTY daemon on {server_host}:{server_port}")

        # Start heartbeat task
        self.heartbeat_task = asyncio.create_task(
            self.websocket_manager.start_heartbeat_task()
        )

        # Configure uvicorn server
        config = uvicorn.Config(
            app=self.app,
            host=server_host,
            port=server_port,
            log_level="info",
            access_log=False,  # Reduce log noise
        )
        server = uvicorn.Server(config)

        # Setup signal handlers
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            asyncio.create_task(self.shutdown())

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        try:
            # Start server
            self.server_task = asyncio.create_task(server.serve())
            logger.info(f"ploTTY daemon started successfully")
            logger.info(f"WebSocket endpoint: ws://{server_host}:{server_port}/ws")
            logger.info(f"Status page: http://{server_host}:{server_port}/")

            # Wait for shutdown
            await self.shutdown_event.wait()

        except Exception as e:
            logger.error(f"Daemon startup failed: {e}")
            raise
        finally:
            await self.shutdown()

    async def shutdown(self):
        """Gracefully shutdown the daemon."""
        logger.info("Shutting down ploTTY daemon...")

        # Signal shutdown
        self.shutdown_event.set()

        # Cancel tasks
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass

        if self.server_task:
            self.server_task.cancel()
            try:
                await self.server_task
            except asyncio.CancelledError:
                pass

        # Close WebSocket connections
        for websocket in list(self.websocket_manager.connections):
            try:
                await websocket.close(code=1000, reason="Server shutdown")
            except Exception:
                pass

        logger.info("ploTTY daemon shutdown complete")


def daemon_command(
    host: str = typer.Option(None, "--host", help="WebSocket host"),
    port: int = typer.Option(None, "--port", help="WebSocket port"),
    foreground: bool = typer.Option(False, "--foreground", help="Run in foreground"),
    config_file: str = typer.Option(None, "--config", help="Config file path"),
) -> None:
    """Run ploTTY as a persistent daemon with WebSocket monitoring."""
    try:
        # Load configuration
        config = load_config(config_file)

        if not config.websocket.enabled:
            typer.echo("WebSocket monitoring is disabled in configuration", err=True)
            typer.echo("Enable it with: websocket.enabled: true", err=True)
            raise typer.Exit(1)

        # Create and start daemon
        daemon = PlottyDaemon(config)

        if foreground:
            # Run in foreground (current process)
            asyncio.run(daemon.start(host, port))
        else:
            # Fork to background (Unix only)
            if sys.platform.startswith("win"):
                typer.echo("Background mode not supported on Windows", err=True)
                typer.echo("Use --foreground flag on Windows", err=True)
                raise typer.Exit(1)

            # Unix fork implementation
            import os

            # First fork
            pid = os.fork()
            if pid > 0:
                # Parent exits
                typer.echo(f"ploTTY daemon started with PID {pid}")
                return

            # Decouple from parent environment
            os.chdir("/")
            os.setsid()
            os.umask(0)

            # Second fork
            pid = os.fork()
            if pid > 0:
                # Parent exits
                return

            # Redirect standard file descriptors
            sys.stdout.flush()
            sys.stderr.flush()
            with open(os.devnull, "w") as devnull:
                os.dup2(devnull.fileno(), sys.stdin.fileno())
                os.dup2(devnull.fileno(), sys.stdout.fileno())
                os.dup2(devnull.fileno(), sys.stderr.fileno())

            # Start daemon in background
            asyncio.run(daemon.start(host, port))

    except KeyboardInterrupt:
        typer.echo("Daemon stopped by user")
    except Exception as e:
        typer.echo(f"Daemon failed to start: {e}", err=True)
        raise typer.Exit(1)


def create_daemon_command() -> typer.Typer:
    """Create daemon command group."""
    daemon_app = typer.Typer(help="Daemon management commands")

    @daemon_app.command("start", help="Start ploTTY daemon")
    def start_daemon(
        host: str = typer.Option(None, "--host", help="WebSocket host"),
        port: int = typer.Option(None, "--port", help="WebSocket port"),
        foreground: bool = typer.Option(
            False, "--foreground", help="Run in foreground"
        ),
        config_file: str = typer.Option(None, "--config", help="Config file path"),
    ):
        """Start ploTTY daemon with WebSocket monitoring."""
        try:
            # Load configuration
            config = load_config(config_file)

            if not config.websocket.enabled:
                typer.echo(
                    "WebSocket monitoring is disabled in configuration", err=True
                )
                typer.echo("Enable it with: websocket.enabled: true", err=True)
                raise typer.Exit(1)

            # Create and start daemon
            daemon = PlottyDaemon(config)

            if foreground:
                # Run in foreground (current process)
                asyncio.run(daemon.start(host, port))
            else:
                # Fork to background (Unix only)
                if sys.platform.startswith("win"):
                    typer.echo("Background mode not supported on Windows", err=True)
                    typer.echo("Use --foreground flag on Windows", err=True)
                    raise typer.Exit(1)

                # Unix fork implementation
                import os

                # First fork
                pid = os.fork()
                if pid > 0:
                    # Parent exits
                    typer.echo(f"ploTTY daemon started with PID {pid}")
                    return

                # Decouple from parent environment
                os.chdir("/")
                os.setsid()
                os.umask(0)

                # Second fork
                pid = os.fork()
                if pid > 0:
                    # Parent exits
                    return

                # Redirect standard file descriptors
                sys.stdout.flush()
                sys.stderr.flush()

                with open("/dev/null", "r") as dev_null:
                    os.dup2(dev_null.fileno(), sys.stdin.fileno())
                with open("/dev/null", "w") as dev_null:
                    os.dup2(dev_null.fileno(), sys.stdout.fileno())
                    os.dup2(dev_null.fileno(), sys.stderr.fileno())

                # Start daemon in background
                asyncio.run(daemon.start(host, port))

        except KeyboardInterrupt:
            typer.echo("Daemon stopped by user")
        except Exception as e:
            typer.echo(f"Daemon failed to start: {e}", err=True)
            raise typer.Exit(1)

    @daemon_app.command("stop", help="Stop ploTTY daemon")
    def stop_daemon():
        """Stop running ploTTY daemon."""
        try:
            import subprocess
            import os

            # Try to find daemon process
            result = subprocess.run(
                ["pgrep", "-f", "plotty.*daemon"], capture_output=True, text=True
            )

            if result.returncode == 0:
                pids = result.stdout.strip().split("\n")
                for pid in pids:
                    if pid.strip():
                        os.kill(int(pid.strip()), signal.SIGTERM)
                        typer.echo(f"Sent SIGTERM to daemon PID {pid}")
                typer.echo("ploTTY daemon stopped")
            else:
                typer.echo("ploTTY daemon not running", err=True)
                raise typer.Exit(1)

        except Exception as e:
            typer.echo(f"Failed to stop daemon: {e}", err=True)
            raise typer.Exit(1)

    @daemon_app.command("status", help="Check daemon status")
    def daemon_status():
        """Check if ploTTY daemon is running."""
        try:
            import subprocess
            import requests

            # Try to find daemon process
            result = subprocess.run(
                ["pgrep", "-f", "plotty.*daemon"], capture_output=True, text=True
            )

            if result.returncode == 0:
                pids = result.stdout.strip().split("\n")
                typer.echo(f"ploTTY daemon running (PIDs: {', '.join(pids)})")

                # Try to check WebSocket server
                try:
                    config = load_config()
                    response = requests.get(
                        f"http://{config.websocket.host}:{config.websocket.port}/status",
                        timeout=5,
                    )
                    if response.status_code == 200:
                        status = response.json()
                        typer.echo(
                            f"WebSocket server: {status['connections']} active connections"
                        )
                    else:
                        typer.echo("WebSocket server: Not responding")
                except Exception:
                    typer.echo("WebSocket server: Connection failed")
            else:
                typer.echo("ploTTY daemon not running")

        except Exception as e:
            typer.echo(f"Failed to check daemon status: {e}", err=True)
            raise typer.Exit(1)

    return daemon_app


# Create daemon app for import
daemon_app = create_daemon_command()
