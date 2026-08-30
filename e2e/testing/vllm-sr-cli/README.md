# vLLM Semantic Router CLI tests

This suite checks the `vllm-sr` command surface and its local container
topology. Unit tests inspect generated commands without starting services;
integration tests start the split Router, Envoy, dashboard, and simulator
images and exercise live APIs.

## Run through Make

From the repository root:

```bash
make vllm-sr-test
make vllm-sr-test-integration
```

`vllm-sr-test` bootstraps the editable CLI and runs without a container
daemon. `vllm-sr-test-integration` builds the required local images and needs
Docker or Podman access.

For a shared host, give the run an isolated stack name and non-overlapping host
port namespace. The same values must be used for the complete run so setup,
assertions, logs, and teardown address one ownership scope:

```bash
make vllm-sr-test-integration VLLM_SR_STACK_NAME=cli-lane-a VLLM_SR_PORT_OFFSET=200
```

The memory integration target accepts the same variables. Do not point an
isolated run at a name or port range already used by another stack.

## What the suite covers

| File | Scope |
| --- | --- |
| `test_unit_serve.py` | Config bootstrap, mounts, ports, image pull policy, tokens, and read-only mode. |
| `test_unit_lifecycle.py` | `status`, `logs`, `stop`, `dashboard`, and `config` command construction. |
| `test_unit_runtime_topology.py` | Split-runtime discovery, cleanup, timeouts, and Docker/Podman selection. |
| `test_integration.py` | Live health, management APIs, model visibility, path rewrites, sidecars, lifecycle, and pull policies. |
| `test_integration_storage_isolation.py` | Redis and Postgres answer on the stack's data network and are unreachable from its application network. |
| `cli_test_base.py` | Shared command and container helpers. |
| `serve_session.py` | Background `vllm-sr serve` orchestration shared by the integration modules. |
| `run_cli_tests.py` | Prerequisite checks, discovery, filtering, and reporting. |

The test files are the source of truth for individual assertions; this README
describes stable areas instead of duplicating every test name.

## Run the test runner directly

Install the editable CLI first, then run from this directory:

```bash
python run_cli_tests.py --verbose
python run_cli_tests.py --verbose --integration
python run_cli_tests.py --pattern lifecycle
```

Set `CONTAINER_RUNTIME=docker` or `CONTAINER_RUNTIME=podman` to select a
runtime. `RUN_INTEGRATION_TESTS=true` also enables integration discovery, but
the `--integration` flag is clearer for direct runs. The Make target supplies
the local image names used by the full integration suite.
