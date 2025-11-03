"""
Hooks execution system for ploTTY FSM state transitions.

This module provides the ability to execute configured hooks when jobs
transition between FSM states, supporting commands, scripts, and webhooks.
"""

from __future__ import annotations
import subprocess
import requests
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class HookExecutionError(Exception):
    """Raised when hook execution fails."""

    pass


class HookExecutor:
    """Executes hooks for FSM state transitions."""

    def __init__(self, job_id: str, workspace: Path):
        """Initialize hook executor for a job.

        Args:
            job_id: Unique job identifier
            workspace: Path to workspace directory
        """
        self.job_id = job_id
        self.workspace = workspace
        self.job_dir = workspace / "jobs" / job_id

    def _substitute_variables(self, template: str, context: Dict[str, Any]) -> str:
        """Substitute variables in hook templates.

        Args:
            template: Template string with {variable} placeholders
            context: Dictionary of variable values

        Returns:
            Template with variables substituted
        """
        try:
            return template.format(**context)
        except KeyError as e:
            raise HookExecutionError(f"Unknown variable in hook template: {e}")

    def _execute_command(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a shell command hook.

        Args:
            command: Command to execute
            context: Variable substitution context

        Returns:
            Execution result
        """
        substituted_cmd = None
        try:
            substituted_cmd = self._substitute_variables(command, context)
            result = subprocess.run(
                substituted_cmd,
                shell=True,  # nosec B602 - needed for user-configured hook commands with variable substitution
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout
            )

            return {
                "type": "command",
                "command": substituted_cmd,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
            }
        except subprocess.TimeoutExpired:
            return {
                "type": "command",
                "command": substituted_cmd or command,
                "error": "Command timed out after 30 seconds",
                "success": False,
            }
        except Exception as e:
            return {
                "type": "command",
                "command": substituted_cmd or command,
                "error": str(e),
                "success": False,
            }
        except subprocess.TimeoutExpired:
            return {
                "type": "command",
                "command": command,
                "error": "Command timed out after 30 seconds",
                "success": False,
            }
        except Exception as e:
            return {
                "type": "command",
                "command": command,
                "error": str(e),
                "success": False,
            }
        except Exception as e:
            return {
                "type": "command",
                "command": command,
                "error": str(e),
                "success": False,
            }
        except Exception as e:
            return {
                "type": "command",
                "command": substituted_cmd,
                "error": str(e),
                "success": False,
            }

    def _execute_script(
        self, script_path: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a script hook.

        Args:
            script_path: Path to script file
            context: Variable substitution context

        Returns:
            Execution result
        """
        substituted_path = None
        try:
            substituted_path = self._substitute_variables(script_path, context)
            script_file = Path(substituted_path)

            if not script_file.exists():
                return {
                    "type": "script",
                    "script": substituted_path,
                    "error": f"Script file not found: {substituted_path}",
                    "success": False,
                }

            # Make script executable
            script_file.chmod(0o755)

            # Execute script with context variables as environment variables
            import os

            env = os.environ.copy()
            env.update({f"PLOTTY_{k.upper()}": str(v) for k, v in context.items()})

            result = subprocess.run(
                [str(script_file)],
                capture_output=True,
                text=True,
                timeout=60,  # 60 second timeout for scripts
                env=env,
            )

            return {
                "type": "script",
                "script": substituted_path,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
            }
        except subprocess.TimeoutExpired:
            return {
                "type": "script",
                "script": substituted_path or script_path,
                "error": "Script timed out after 60 seconds",
                "success": False,
            }
        except Exception as e:
            return {
                "type": "script",
                "script": substituted_path or script_path,
                "error": str(e),
                "success": False,
            }

            # Make script executable
            script_file.chmod(0o755)

            # Execute script with context variables as environment variables
            import os

            env = os.environ.copy()
            env.update({f"PLOTTY_{k.upper()}": str(v) for k, v in context.items()})

            result = subprocess.run(
                [str(script_file)],
                capture_output=True,
                text=True,
                timeout=60,  # 60 second timeout for scripts
                env=env,
            )

            return {
                "type": "script",
                "script": substituted_path,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
            }
        except subprocess.TimeoutExpired:
            return {
                "type": "script",
                "script": substituted_path,
                "error": "Script timed out after 60 seconds",
                "success": False,
            }
        except Exception as e:
            return {
                "type": "script",
                "script": substituted_path,
                "error": str(e),
                "success": False,
            }

    def _execute_webhook(
        self, webhook_url: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a webhook hook.

        Args:
            webhook_url: URL to POST webhook to
            context: Variable substitution context

        Returns:
            Execution result
        """
        substituted_url = None
        try:
            substituted_url = self._substitute_variables(webhook_url, context)

            payload = {
                "job_id": self.job_id,
                "event": "state_transition",
                "context": context,
            }

            response = requests.post(
                substituted_url,
                json=payload,
                timeout=10,  # 10 second timeout
            )

            return {
                "type": "webhook",
                "url": substituted_url,
                "status_code": response.status_code,
                "response_text": response.text,
                "success": 200 <= response.status_code < 300,
            }
        except requests.exceptions.Timeout:
            return {
                "type": "webhook",
                "url": substituted_url or webhook_url,
                "error": "Webhook timed out after 10 seconds",
                "success": False,
            }
        except Exception as e:
            return {
                "type": "webhook",
                "url": substituted_url or webhook_url,
                "error": str(e),
                "success": False,
            }

            response = requests.post(
                substituted_url,
                json=payload,
                timeout=10,  # 10 second timeout
            )

            return {
                "type": "webhook",
                "url": substituted_url,
                "status_code": response.status_code,
                "response_text": response.text,
                "success": 200 <= response.status_code < 300,
            }
        except requests.exceptions.Timeout:
            return {
                "type": "webhook",
                "url": substituted_url,
                "error": "Webhook timed out after 10 seconds",
                "success": False,
            }
        except Exception as e:
            return {
                "type": "webhook",
                "url": substituted_url,
                "error": str(e),
                "success": False,
            }

    def execute_hooks(
        self, hooks: List[Dict[str, str]], context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute a list of hooks.

        Args:
            hooks: List of hook configurations
            context: Variable substitution context

        Returns:
            List of execution results
        """
        results = []

        for hook in hooks:
            hook_type = None
            hook_target = None

            # Determine hook type and target
            if "command" in hook:
                hook_type = "command"
                hook_target = hook["command"]
            elif "script" in hook:
                hook_type = "script"
                hook_target = hook["script"]
            elif "webhook" in hook:
                hook_type = "webhook"
                hook_target = hook["webhook"]
            else:
                logger.warning(f"Unknown hook type: {hook}")
                continue

            # Execute hook based on type
            if hook_type == "command":
                result = self._execute_command(hook_target, context)
            elif hook_type == "script":
                result = self._execute_script(hook_target, context)
            elif hook_type == "webhook":
                result = self._execute_webhook(hook_target, context)
            else:
                continue

            results.append(result)

            # Log result
            if result["success"]:
                logger.info(f"Hook executed successfully: {hook_type} - {hook_target}")
            else:
                logger.error(
                    f"Hook execution failed: {hook_type} - {hook_target} - {result.get('error', 'Unknown error')}"
                )

        return results

    def get_context(
        self, state: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get variable substitution context for hooks.

        Args:
            state: Current FSM state
            metadata: Additional metadata from state transition

        Returns:
            Context dictionary for variable substitution
        """
        context = {
            "job_id": self.job_id,
            "job_path": str(self.job_dir),
            "state": state,
            "workspace": str(self.workspace),
        }

        # Add job metadata if available
        job_file = self.job_dir / "job.json"
        if job_file.exists():
            with open(job_file, "r") as f:
                job_data = json.load(f)
            context.update(job_data)

        # Add transition metadata
        if metadata:
            context.update(metadata)

        return context


def create_hook_executor(job_id: str, workspace: Path) -> HookExecutor:
    """Factory function to create hook executor.

    Args:
        job_id: Unique job identifier
        workspace: Path to workspace directory

    Returns:
        HookExecutor instance
    """
    return HookExecutor(job_id, workspace)
