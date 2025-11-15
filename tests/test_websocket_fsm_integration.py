#!/usr/bin/env python3
"""
WebSocket FSM integration tests for ploTTY monitoring system.

This module tests the integration between FSM state changes and WebSocket
broadcasting through the HookExecutor system.
"""

import asyncio
import tempfile
import time
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from plotty.fsm import JobFSM, JobState
from plotty.hooks import HookExecutor
from plotty.config import load_config
from plotty.websocket.server import WebSocketManager, create_websocket_app
import websockets
import json


class WebSocketFSMTestEnvironment:
    """Test environment for WebSocket-FSM integration testing."""

    def __init__(self):
        self.daemon_task = None
        self.websocket_manager = None
        self.fsm = None
        self.hook_executor = None
        self.temp_dir = None

    async def setup(self, port=8767):
        """Setup complete test environment."""
        # Create temporary workspace and config
        self.temp_dir = Path(tempfile.mkdtemp())
        workspace = self.temp_dir / "workspace"
        workspace.mkdir()

        config_file = self.temp_dir / "config.yaml"
        config_file.write_text(
            f"""
workspace: {workspace}
database: {{ url: "sqlite:///{workspace}/test.db" }}
websocket:
  enabled: true
  host: localhost
  port: {port}
  authenticate: false

hooks:
  NEW:
    - command: "echo 'Job {{job_id}} created'"
  READY:
    - command: "echo 'Job {{job_id}} ready'"
  QUEUED:
    - command: "echo 'Job {{job_id}} queued'"
"""
        )

        # Load config
        config = load_config(str(config_file))

        # Setup WebSocket manager
        self.websocket_manager = WebSocketManager(config.websocket)

        # Inject WebSocket manager into HookExecutor class
        HookExecutor.websocket_manager = self.websocket_manager

        # Start WebSocket daemon
        app = create_websocket_app(self.websocket_manager)
        import uvicorn

        server_config = uvicorn.Config(
            app, host="localhost", port=port, log_level="error"
        )
        self.daemon_task = asyncio.create_task(uvicorn.Server(server_config).serve())

        # Wait for server to start
        await asyncio.sleep(0.5)

        # Create FSM and HookExecutor
        self.fsm = JobFSM("test_job_fsm", workspace)
        self.hook_executor = HookExecutor("test_job_fsm", workspace)

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

    async def create_websocket_client(self, port=8767):
        """Create WebSocket client to monitor messages."""
        uri = f"ws://localhost:{port}/ws"
        websocket = await websockets.connect(uri)

        # Subscribe to jobs channel
        subscribe_msg = {"type": "SUBSCRIBE", "channels": ["jobs"]}
        await websocket.send(json.dumps(subscribe_msg))

        return websocket


def create_test_result(test_name: str, passed: bool, message: str) -> dict:
    """Create standardized test result."""
    return {
        "test": test_name,
        "passed": passed,
        "message": message,
        "timestamp": time.time(),
    }


async def test_fsm_state_change_broadcasting():
    """Test FSM state changes broadcast to WebSocket clients."""
    env = WebSocketFSMTestEnvironment()
    try:
        await env.setup()

        # Create WebSocket client to monitor
        websocket = await env.create_websocket_client()

        # Trigger FSM state change
        success = env.fsm.transition_to(JobState.READY, reason="Test transition")

        if not success:
            return create_test_result(
                "WebSocket: FSM state broadcasting",
                False,
                "✗ FSM state transition failed",
            )

        # Wait for WebSocket message
        try:
            message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
            message_data = json.loads(message)

            # Verify message content
            if (
                message_data.get("type") == "job_state_change"
                and message_data.get("job_id") == "test_job_fsm"
                and message_data.get("to_state") == "READY"
            ):
                return create_test_result(
                    "WebSocket: FSM state broadcasting",
                    True,
                    "✓ FSM state change broadcasted successfully",
                )
            else:
                return create_test_result(
                    "WebSocket: FSM state broadcasting",
                    False,
                    f"✗ Incorrect message content: {message_data}",
                )

        except asyncio.TimeoutError:
            return create_test_result(
                "WebSocket: FSM state broadcasting",
                False,
                "✗ Timeout waiting for state change broadcast",
            )

    except Exception as e:
        return create_test_result(
            "WebSocket: FSM state broadcasting", False, f"✗ Test failed: {str(e)}"
        )
    finally:
        try:
            await websocket.close()
        except:
            pass
        await env.cleanup()


async def test_hook_executor_websocket_integration():
    """Test HookExecutor creates and sends WebSocket messages."""
    env = WebSocketFSMTestEnvironment()
    try:
        await env.setup()

        # Create WebSocket client
        websocket = await env.create_websocket_client()

        # Manually trigger hook execution with WebSocket context
        context = {
            "job_id": "hook_test_job",
            "from_state": "NEW",
            "to_state": "READY",
            "reason": "Hook integration test",
            "event": "state_change",
        }

        # Execute hooks (should trigger WebSocket broadcast)
        hooks = [{"command": "echo 'test hook'"}]
        results = env.hook_executor.execute_hooks(hooks, context)

        # Wait for WebSocket message
        try:
            message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
            message_data = json.loads(message)

            if message_data.get("type") == "job_state_change":
                return create_test_result(
                    "WebSocket: Hook integration",
                    True,
                    "✓ HookExecutor WebSocket integration working",
                )
            else:
                return create_test_result(
                    "WebSocket: Hook integration",
                    False,
                    f"✗ Unexpected message type: {message_data.get('type')}",
                )

        except asyncio.TimeoutError:
            return create_test_result(
                "WebSocket: Hook integration",
                False,
                "✗ Hook did not trigger WebSocket broadcast",
            )

    except Exception as e:
        return create_test_result(
            "WebSocket: Hook integration",
            False,
            f"✗ Hook integration test failed: {str(e)}",
        )
    finally:
        try:
            await websocket.close()
        except:
            pass
        await env.cleanup()


async def test_job_lifecycle_monitoring():
    """Test complete job lifecycle monitoring via WebSocket."""
    env = WebSocketFSMTestEnvironment()
    try:
        await env.setup()

        # Create WebSocket client
        websocket = await env.create_websocket_client()

        # Track received state changes
        received_states = []

        async def collect_messages():
            try:
                while True:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    message_data = json.loads(message)
                    if message_data.get("type") == "job_state_change":
                        received_states.append(message_data.get("to_state"))
            except asyncio.TimeoutError:
                break

        # Start message collection
        collector_task = asyncio.create_task(collect_messages())

        # Trigger multiple state changes
        state_sequence = [JobState.READY, JobState.QUEUED, JobState.ARMED]
        for state in state_sequence:
            success = env.fsm.transition_to(
                state, reason=f"Transition to {state.value}"
            )
            if not success:
                collector_task.cancel()
                return create_test_result(
                    "WebSocket: Job lifecycle monitoring",
                    False,
                    f"✗ Failed to transition to {state.value}",
                )
            await asyncio.sleep(0.2)  # Brief pause between transitions

        # Wait for message collection
        await collector_task

        # Verify we received all state changes
        expected_states = [s.value for s in state_sequence]
        if all(state in received_states for state in expected_states):
            return create_test_result(
                "WebSocket: Job lifecycle monitoring",
                True,
                f"✓ Successfully monitored {len(received_states)} state changes",
            )
        else:
            return create_test_result(
                "WebSocket: Job lifecycle monitoring",
                False,
                f"✗ Missing states. Expected: {expected_states}, Received: {received_states}",
            )

    except Exception as e:
        return create_test_result(
            "WebSocket: Job lifecycle monitoring",
            False,
            f"✗ Lifecycle monitoring test failed: {str(e)}",
        )
    finally:
        try:
            await websocket.close()
        except:
            pass
        await env.cleanup()


# Test runner functions for integration with check self
async def run_websocket_fsm_tests(test_env: dict, progress_tracker=None) -> list:
    """Run WebSocket-FSM integration tests."""
    results = []

    if progress_tracker:
        progress_tracker.advance("WebSocket: FSM state broadcasting")
    result = await test_fsm_state_change_broadcasting()
    results.append(result)

    if progress_tracker:
        progress_tracker.advance("WebSocket: Hook integration")
    result = await test_hook_executor_websocket_integration()
    results.append(result)

    if progress_tracker:
        progress_tracker.advance("WebSocket: Job lifecycle monitoring")
    result = await test_job_lifecycle_monitoring()
    results.append(result)

    return results


if __name__ == "__main__":
    # Run tests standalone for development
    async def run_all_tests():
        tests = [
            test_fsm_state_change_broadcasting,
            test_hook_executor_websocket_integration,
            test_job_lifecycle_monitoring,
        ]

        for test_func in tests:
            result = await test_func()
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"{status}: {result['test']}")
            print(f"   {result['message']}")
            print()

    asyncio.run(run_all_tests())
