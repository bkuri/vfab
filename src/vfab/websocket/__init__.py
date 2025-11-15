"""
WebSocket package for vfab real-time monitoring.

This package provides WebSocket server functionality and message schemas
for real-time communication between vfab daemon and monitoring clients.
"""

from .server import WebSocketManager, create_websocket_app
from .schemas import (
    Channel,
    MessageType,
    JobStateChangeMessage,
    JobProgressMessage,
    DeviceStatusMessage,
    SystemAlertMessage,
    ErrorMessage,
    PongMessage,
    get_channels_for_message,
)

__all__ = [
    "WebSocketManager",
    "create_websocket_app",
    "Channel",
    "MessageType",
    "JobStateChangeMessage",
    "JobProgressMessage",
    "DeviceStatusMessage",
    "SystemAlertMessage",
    "ErrorMessage",
    "PongMessage",
    "get_channels_for_message",
]
