"""
WebSocket server for ploTTY real-time monitoring.

This module provides WebSocket server functionality that integrates with
the existing hook system to broadcast real-time events to monitoring clients.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Dict, Set, Any, Optional
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from ..config import WebSocketCfg
from .schemas import (
    Channel,
    MessageType,
    PongMessage,
    ErrorMessage,
    ServerMessage,
    get_channels_for_message,
    validate_message_channels,
)

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and message broadcasting."""

    def __init__(self, config: WebSocketCfg):
        self.config = config
        self.connections: Set[WebSocket] = set()
        self.subscriptions: Dict[WebSocket, Set[Channel]] = {}
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        self._connection_id_counter = 0

    def _get_connection_id(self) -> int:
        """Generate unique connection ID."""
        self._connection_id_counter += 1
        return self._connection_id_counter

    async def connect(self, websocket: WebSocket) -> int:
        """Accept and register a new WebSocket connection."""
        await websocket.accept()

        # Check connection limit
        if len(self.connections) >= self.config.max_connections:
            await websocket.close(code=1013, reason="Server overloaded")
            return -1

        self.connections.add(websocket)
        connection_id = self._get_connection_id()
        self.subscriptions[websocket] = {Channel.ALL}  # Default to all channels
        self.connection_metadata[websocket] = {
            "connection_id": connection_id,
            "connected_at": datetime.utcnow(),
            "last_ping": datetime.utcnow(),
        }

        logger.info(
            f"WebSocket client {connection_id} connected "
            f"(total connections: {len(self.connections)})"
        )

        return connection_id

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        if websocket in self.connections:
            connection_id = self.connection_metadata.get(websocket, {}).get(
                "connection_id", "unknown"
            )
            self.connections.discard(websocket)
            self.subscriptions.pop(websocket, None)
            self.connection_metadata.pop(websocket, None)

            logger.info(
                f"WebSocket client {connection_id} disconnected "
                f"(total connections: {len(self.connections)})"
            )

    async def handle_message(
        self, websocket: WebSocket, message_data: Dict[str, Any]
    ) -> Optional[ServerMessage]:
        """Handle incoming message from client."""
        try:
            print(f"DEBUG: Received message_data: {message_data}")
            message_type = message_data.get("type")
            print(f"DEBUG: message_type: {message_type} (type: {type(message_type)})")
            print(f"DEBUG: MessageType.SUBSCRIBE.value: {MessageType.SUBSCRIBE.value}")

            if message_type == MessageType.SUBSCRIBE.value:
                return await self._handle_subscribe(websocket, message_data)
            elif message_type == MessageType.UNSUBSCRIBE.value:
                return await self._handle_unsubscribe(websocket, message_data)
            elif message_type == MessageType.PING.value:
                return await self._handle_ping(websocket)
            else:
                return ErrorMessage(
                    type=MessageType.ERROR,
                    error_code="UNKNOWN_MESSAGE_TYPE",
                    error_message=f"Unknown message type: {message_type}",
                )

        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            return ErrorMessage(
                type=MessageType.ERROR,
                error_code="MESSAGE_HANDLING_ERROR",
                error_message=str(e),
            )

    async def _handle_subscribe(
        self, websocket: WebSocket, data: Dict[str, Any]
    ) -> Optional[ServerMessage]:
        """Handle channel subscription request."""
        try:
            channels = validate_message_channels(data.get("channels", []))
            self.subscriptions[websocket] = set(channels)

            logger.debug(
                f"Client {self.connection_metadata[websocket]['connection_id']} "
                f"subscribed to channels: {[c.value for c in channels]}"
            )

            return None  # No response needed for successful subscription

        except Exception as e:
            return ErrorMessage(
                type=MessageType.ERROR,
                error_code="SUBSCRIPTION_ERROR",
                error_message=str(e),
            )

    async def _handle_unsubscribe(
        self, websocket: WebSocket, data: Dict[str, Any]
    ) -> Optional[ServerMessage]:
        """Handle channel unsubscription request."""
        try:
            channels = validate_message_channels(data.get("channels", []))
            current_subs = self.subscriptions.get(websocket, set())

            # Remove specified channels
            for channel in channels:
                current_subs.discard(channel)

            # Ensure at least one channel subscription
            if not current_subs:
                current_subs.add(Channel.ALL)

            self.subscriptions[websocket] = current_subs

            logger.debug(
                f"Client {self.connection_metadata[websocket]['connection_id']} "
                f"unsubscribed from channels: {[c.value for c in channels]}"
            )

            return None

        except Exception as e:
            return ErrorMessage(error_code="UNSUBSCRIPTION_ERROR", error_message=str(e))

    async def _handle_ping(self, websocket: WebSocket) -> PongMessage:
        """Handle ping message."""
        self.connection_metadata[websocket]["last_ping"] = datetime.utcnow()
        return PongMessage()

    async def broadcast(
        self, message: ServerMessage, channel: Optional[Channel] = None
    ) -> None:
        """Broadcast message to subscribed clients."""
        if not self.connections:
            return

        # Determine which channels this message should go to
        target_channels = (
            [channel] if channel else get_channels_for_message(message.type)
        )

        # Serialize message once for efficiency
        message_json = message.model_dump_json()

        # Send to appropriate subscribers
        disconnected_clients = []
        for websocket in self.connections:
            try:
                # Check if client is subscribed to any target channel
                client_channels = self.subscriptions.get(websocket, {Channel.ALL})

                should_send = Channel.ALL in client_channels or any(
                    target_channel in client_channels
                    for target_channel in target_channels
                )

                if should_send:
                    await websocket.send_text(message_json)

            except Exception as e:
                logger.warning(f"Failed to send message to client: {e}")
                disconnected_clients.append(websocket)

        # Clean up disconnected clients
        for websocket in disconnected_clients:
            self.disconnect(websocket)

    async def start_heartbeat_task(self) -> None:
        """Start background task for connection health monitoring."""
        while True:
            try:
                await asyncio.sleep(self.config.heartbeat_interval)

                # Check for stale connections
                now = datetime.utcnow()
                stale_clients = []

                for websocket, metadata in self.connection_metadata.items():
                    last_ping = metadata.get(
                        "last_ping", metadata.get("connected_at", now)
                    )
                    if (now - last_ping).seconds > self.config.heartbeat_interval * 2:
                        stale_clients.append(websocket)

                # Disconnect stale clients
                for websocket in stale_clients:
                    logger.info(
                        f"Disconnecting stale client {metadata['connection_id']}"
                    )
                    try:
                        await websocket.close(code=1000, reason="Heartbeat timeout")
                    except Exception:
                        pass
                    self.disconnect(websocket)

            except Exception as e:
                logger.error(f"Error in heartbeat task: {e}")
                await asyncio.sleep(5)  # Brief pause before retry

    def get_status(self) -> Dict[str, Any]:
        """Get current server status."""
        return {
            "connections": len(self.connections),
            "max_connections": self.config.max_connections,
            "subscriptions": {
                str(conn_id): [ch.value for ch in channels]
                for conn_id, channels in (
                    (metadata["connection_id"], subs)
                    for metadata, subs in (
                        (
                            self.connection_metadata.get(ws, {}),
                            self.subscriptions.get(ws, set()),
                        )
                        for ws in self.connections
                    )
                )
            },
        }


def create_websocket_app(manager: WebSocketManager) -> FastAPI:
    """Create FastAPI application with WebSocket endpoint."""
    app = FastAPI(
        title="ploTTY WebSocket API",
        description="Real-time monitoring API for ploTTY plotting system",
        version="1.1.3",
    )

    @app.get("/", response_class=HTMLResponse)
    async def get_status_page():
        """Simple status page for WebSocket server."""
        status = manager.get_status()
        return f"""
        <html>
            <head><title>ploTTY WebSocket Server</title></head>
            <body>
                <h1>ploTTY WebSocket Server</h1>
                <p>Active connections: {status["connections"]}/{status["max_connections"]}</p>
                <p>WebSocket endpoint: <code>ws://localhost:8765/ws</code></p>
                <h2>Subscriptions</h2>
                <pre>{json.dumps(status["subscriptions"], indent=2)}</pre>
            </body>
        </html>
        """

    @app.get("/status")
    async def get_status():
        """Get server status as JSON."""
        return manager.get_status()

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """Main WebSocket endpoint for real-time monitoring."""
        connection_id = await manager.connect(websocket)
        if connection_id == -1:
            return  # Connection rejected

        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                print(f"DEBUG: WebSocket received raw data: {data}")
                message_data = json.loads(data)
                print(f"DEBUG: Parsed message_data: {message_data}")

                # Handle message and get response if any
                response = await manager.handle_message(websocket, message_data)
                print(f"DEBUG: Manager response: {response}")

                # Send response if message handling produced one
                if response:
                    await websocket.send_text(response.model_dump_json())

        except WebSocketDisconnect:
            logger.debug(f"WebSocket client {connection_id} disconnected normally")
        except Exception as e:
            logger.error(f"WebSocket error for client {connection_id}: {e}")
        finally:
            manager.disconnect(websocket)

    return app
