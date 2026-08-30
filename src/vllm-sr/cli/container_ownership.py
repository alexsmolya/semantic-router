"""Ownership attestation for containers and networks managed by a stack."""

import json
import subprocess

from cli.container_runtime import get_container_runtime
from cli.runtime_stack import (
    MANAGED_RESOURCE_LABEL,
    RUN_RESOURCE_LABEL,
    STACK_RESOURCE_LABEL,
)


def labels_match_ownership(
    labels: object,
    stack_name: str,
    run_id: str | None = None,
) -> bool:
    """Return whether labels attest ownership of the requested stack/run.

    A missing run id means legacy stack mode. It intentionally does not adopt
    a resource carrying a run label: an explicitly isolated run must not be
    stopped accidentally by a later stack-only command.
    """
    if not isinstance(labels, dict):
        return False
    if labels.get(MANAGED_RESOURCE_LABEL) != "true":
        return False
    if labels.get(STACK_RESOURCE_LABEL) != stack_name:
        return False
    actual_run_id = labels.get(RUN_RESOURCE_LABEL)
    if run_id is None:
        return actual_run_id is None
    return actual_run_id == run_id


def _inspect_labels(resource_kind: str, resource_name: str) -> tuple[str, object]:
    """Inspect labels and distinguish absence from an unknown answer."""
    runtime = get_container_runtime()
    if resource_kind == "container":
        command = [
            runtime,
            "inspect",
            "--format",
            "{{json .Config.Labels}}",
            resource_name,
        ]
        missing_markers = ("no such container", "no such object")
    else:
        command = [
            runtime,
            "network",
            "inspect",
            "--format",
            "{{json .Labels}}",
            resource_name,
        ]
        missing_markers = ("no such network", "network not found")
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, check=False, timeout=10
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown", None
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).lower()
        return (
            "not found"
            if any(marker in detail for marker in missing_markers)
            else "unknown",
            None,
        )
    try:
        labels = json.loads(result.stdout or "null")
    except json.JSONDecodeError:
        return "unknown", None
    return "inspected", labels


def container_ownership(
    container_name: str, stack_name: str, run_id: str | None = None
) -> str:
    """Return whether a named container is owned by the requested stack/run."""
    status, labels = _inspect_labels("container", container_name)
    if status != "inspected":
        return status
    return "owned" if labels_match_ownership(labels, stack_name, run_id) else "unowned"


def network_ownership(
    network_name: str, stack_name: str, run_id: str | None = None
) -> str:
    """Return whether a named network is owned by the requested stack/run."""
    status, labels = _inspect_labels("network", network_name)
    if status != "inspected":
        return status
    return "owned" if labels_match_ownership(labels, stack_name, run_id) else "unowned"
