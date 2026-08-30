"""Ownership attestation for containers and networks managed by a stack."""

import json
import subprocess

from cli.container_runtime import get_container_runtime


def container_ownership(container_name: str, stack_name: str) -> str:
    """Return whether a named container is owned by the requested stack."""
    runtime = get_container_runtime()
    try:
        result = subprocess.run(
            [runtime, "inspect", "--format", "{{json .Config.Labels}}", container_name],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).lower()
        if any(marker in detail for marker in ("no such container", "no such object")):
            return "not found"
        return "unknown"
    try:
        labels = json.loads(result.stdout or "null")
    except json.JSONDecodeError:
        return "unknown"
    if not isinstance(labels, dict):
        return "unowned"
    if labels.get("com.vllm.semantic-router.managed") != "true":
        return "unowned"
    if labels.get("com.vllm.semantic-router.stack") != stack_name:
        return "unowned"
    return "owned"


def network_ownership(network_name: str, stack_name: str) -> str:
    """Return whether a named network is owned by the requested stack."""
    runtime = get_container_runtime()
    try:
        result = subprocess.run(
            [
                runtime,
                "network",
                "inspect",
                "--format",
                "{{json .Labels}}",
                network_name,
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).lower()
        if any(marker in detail for marker in ("no such network", "network not found")):
            return "not found"
        return "unknown"
    try:
        labels = json.loads(result.stdout or "null")
    except json.JSONDecodeError:
        return "unknown"
    if not isinstance(labels, dict):
        return "unowned"
    if labels.get("com.vllm.semantic-router.managed") != "true":
        return "unowned"
    if labels.get("com.vllm.semantic-router.stack") != stack_name:
        return "unowned"
    return "owned"
