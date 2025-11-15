#!/usr/bin/env python3
"""
WebSocket integration tests for vfab monitoring system.

This module tests core WebSocket functionality including server startup,
message validation, channel subscriptions, and multi-client support.
"""

import asyncio
import json
import tempfile
import time
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import websockets
from vfab.config import load_config
from vfab.websocket.server import WebSocketManager, create_websocket_app
from vfab.websocket.schemas import (
    JobStateChangeMessage,
    Channel,
)


class WebSocketTestEnvironment:
    """Test environment for WebSocket testing."""

    def __init__(self):
        self.daemon_task = None
        self.websocket_manager = None
        self.temp_dir = None

    async def setup_daemon(self, port=8766):
        """Start WebSocket daemon for testing."""
        # Create temporary config
        self.temp_dir = Path(tempfile.mkdtemp())
        config_file = self.temp_dir / "config.yaml"
        config_file.write_text(
            f"""
workspace: {self.temp_dir}/workspace
database: {{ url: "sqlite:///{self.temp_dir}/test.db" }}
websocket:
  enabled: true
  host: localhost
  port: {port}
  authenticate: false
"""
        )

        # Load config and create WebSocket manager
        config = load_config(str(config_file))
        self.websocket_manager = WebSocketManager(config.websocket)
        app = create_websocket_app(self.websocket_manager)

        # Start server in background
        import uvicorn

        server_config = uvicorn.Config(
            app, host="localhost", port=port, log_level="error"
        )
        self.daemon_task = asyncio.create_task(uvicorn.Server(server_config).serve())

        # Wait for server to start
        await asyncio.sleep(0.5)

    async def cleanup(self):
        """Clean up test environment."""
        if self.daemon_task:
            self.daemon_task.cancel()
            try:
                await self.daemon_task
            except asyncio.CancelledError:
                pass

        if self.temp_dir and self.temp_dir.exists():
            import shutil

            shutil.rmtree(self.temp_dir, ignore_errors=True)

    async def create_client(self, port=8766):
        """Create WebSocket client connection."""
        uri = f"ws://localhost:{port}/ws"
        return await websockets.connect(uri)

    async def subscribe_to_channel(self, websocket, channel):
        """Subscribe to specific channel."""
        subscribe_msg = {"type": "SUBSCRIBE", "channels": [channel]}
        await websocket.send(json.dumps(subscribe_msg))


def create_test_result(test_name: str, passed: bool, message: str) -> dict:
    """Create standardized test result."""
    return {
        "test": test_name,
        "passed": passed,
        "message": message,
        "timestamp": time.time(),
    }


async def test_websocket_server_startup():
    """Test WebSocket server starts and accepts connections."""
    env = WebSocketTestEnvironment()
    try:
        await env.setup_daemon()

        # Test connection
        websocket = await env.create_client()
        await websocket.close()

        return create_test_result(
            "WebSocket: Server startup",
            True,
            "✓ WebSocket server started and accepted connections",
        )
    except Exception as e:
        return create_test_result(
            "WebSocket: Server startup",
            False,
            f"✗ Failed to start WebSocket server: {str(e)}",
        )
    finally:
        await env.cleanup()


async def test_websocket_message_schemas():
    """Test WebSocket message validation and schemas."""
    env = WebSocketTestEnvironment()
    try:
        await env.setup_daemon()

        # Create test message
        test_message = JobStateChangeMessage(
            job_id="test_job_123",
            from_state="NEW",
            to_state="READY",
            reason="Test message",
            metadata={"test": True},
        )

        # Validate message serialization
        message_json = test_message.model_dump_json()
        parsed_message = json.loads(message_json)

        # Verify required fields
        required_fields = ["type", "timestamp", "job_id", "to_state"]
        missing_fields = [
            field for field in required_fields if field not in parsed_message
        ]

        if missing_fields:
            return create_test_result(
                "WebSocket: Message schemas",
                False,
                f"✗ Missing required fields: {missing_fields}",
            )

        return create_test_result(
            "WebSocket: Message schemas",
            True,
            "✓ WebSocket message schemas validated successfully",
        )
    except Exception as e:
        return create_test_result(
            "WebSocket: Message schemas",
            False,
            f"✗ Message schema validation failed: {str(e)}",
        )
    finally:
        await env.cleanup()


async def test_websocket_channel_subscriptions():
    """Test channel subscription and message routing."""
    env = WebSocketTestEnvironment()
    try:
        await env.setup_daemon()

        # Create client and subscribe to jobs channel
        websocket = await env.create_client()
        await env.subscribe_to_channel(websocket, "jobs")

        # Send test message to jobs channel
        test_message = JobStateChangeMessage(
            job_id="test_job_456",
            from_state="READY",
            to_state="QUEUED",
            reason="Channel test",
        )

        await env.websocket_manager.broadcast(test_message, Channel.JOBS)

        # Receive message
        response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
        response_data = json.loads(response)

        # Verify message content
        if response_data.get("job_id") == "test_job_456":
            return create_test_result(
                "WebSocket: Channel subscriptions",
                True,
                "✓ Channel subscription and message routing working",
            )
        else:
            return create_test_result(
                "WebSocket: Channel subscriptions",
                False,
                "✗ Received incorrect message on subscribed channel",
            )
    except asyncio.TimeoutError:
        return create_test_result(
            "WebSocket: Channel subscriptions",
            False,
            "✗ Timeout waiting for message on subscribed channel",
        )
    except Exception as e:
        return create_test_result(
            "WebSocket: Channel subscriptions",
            False,
            f"✗ Channel subscription test failed: {str(e)}",
        )
    finally:
        await env.cleanup()


async def test_websocket_multi_client():
    """Test multiple simultaneous monitor connections."""
    env = WebSocketTestEnvironment()
    try:
        await env.setup_daemon()

        # Create multiple clients
        clients = []
        for i in range(3):
            client = await env.create_client()
            await env.subscribe_to_channel(client, "jobs")
            clients.append(client)

        # Broadcast message
        test_message = JobStateChangeMessage(
            job_id="multi_client_test",
            from_state="QUEUED",
            to_state="ARMED",
            reason="Multi-client test",
        )

        await env.websocket_manager.broadcast(test_message, Channel.JOBS)

        # All clients should receive the message
        received_count = 0
        for client in clients:
            try:
                response = await asyncio.wait_for(client.recv(), timeout=2.0)
                response_data = json.loads(response)
                if response_data.get("job_id") == "multi_client_test":
                    received_count += 1
            except asyncio.TimeoutError:
                pass

        # Close all clients
        for client in clients:
            await client.close()

        if received_count == 3:
            return create_test_result(
                "WebSocket: Multi-client support",
                True,
                "✓ All 3 clients received broadcast message",
            )
        else:
            return create_test_result(
                "WebSocket: Multi-client support",
                False,
                f"✗ Only {received_count}/3 clients received message",
            )
    except Exception as e:
        return create_test_result(
            "WebSocket: Multi-client support",
            False,
            f"✗ Multi-client test failed: {str(e)}",
        )
    finally:
        await env.cleanup()


# Test runner functions for integration with check self
async def run_websocket_basic_tests(test_env: dict, progress_tracker=None) -> list:
    """Run basic WebSocket functionality tests."""
    results = []

    if progress_tracker:
        progress_tracker.advance("WebSocket: Server startup")
    result = await test_websocket_server_startup()
    results.append(result)

    if progress_tracker:
        progress_tracker.advance("WebSocket: Message schemas")
    result = await test_websocket_message_schemas()
    results.append(result)

    return results


async def run_websocket_advanced_tests(test_env: dict, progress_tracker=None) -> list:
    """Run advanced WebSocket integration tests."""
    results = []

    if progress_tracker:
        progress_tracker.advance("WebSocket: Channel subscriptions")
    result = await test_websocket_channel_subscriptions()
    results.append(result)

    if progress_tracker:
        progress_tracker.advance("WebSocket: Multi-client support")
    result = await test_websocket_multi_client()
    results.append(result)

    return results


if __name__ == "__main__":
    # Run tests standalone for development
    async def run_all_tests():
        tests = [
            test_websocket_server_startup,
            test_websocket_message_schemas,
            test_websocket_channel_subscriptions,
            test_websocket_multi_client,
        ]

        for test_func in tests:
            result = await test_func()
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"{status}: {result['test']}")
            print(f"   {result['message']}")
            print()

    asyncio.run(run_all_tests())
