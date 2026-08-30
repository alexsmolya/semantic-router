"""Create and attest networks used by a local runtime stack."""

import subprocess

from cli.container_ownership import network_ownership
from cli.container_runtime import get_container_runtime
from cli.utils import get_logger

log = get_logger(__name__)


def container_create_network(network_name, labels=()):
    """Create a Docker network if it doesn't exist."""
    runtime = get_container_runtime()
    cmd = [
        runtime,
        "network",
        "ls",
        "--filter",
        f"name={network_name}",
        "--format",
        "{{.Name}}",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        existing_networks = {
            line.strip() for line in result.stdout.splitlines() if line.strip()
        }
        if network_name in existing_networks:
            if labels:
                expected = dict(labels)
                stack_name = expected.get("com.vllm.semantic-router.stack", "")
                run_id = expected.get("com.vllm.semantic-router.run")
                ownership = network_ownership(network_name, stack_name, run_id)
                if ownership != "owned":
                    return (
                        1,
                        "",
                        f"refusing to adopt network {network_name}: ownership is {ownership}",
                    )
            log.debug(f"Network {network_name} already exists")
            return (0, "", "")
    except subprocess.CalledProcessError:
        pass

    cmd = [runtime, "network", "create"]
    for key, value in labels:
        cmd.extend(["--label", f"{key}={value}"])
    cmd.append(network_name)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        log.info(f"Created network: {network_name}")
        return (0, result.stdout, result.stderr)
    except subprocess.CalledProcessError as exc:
        return (exc.returncode, exc.stdout, exc.stderr)
