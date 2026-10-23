# Agent-assisted engineering workflow

This example records an AI-assisted maintenance change in Automation Kit. Stefan set the cleanup objective and publication boundaries; Codex inspected the implementation, wrote the repair and tests, and checked the result. Automated code review is identified separately from human direction.

## Specification and context

The requirement was to verify the real MCP stdio path, beyond the existing direct handler tests. The working context was limited to the server, package contract, related tests and official SDK source. Supplied fixtures were used; no provider account configuration was needed.

The interface keeps discovery separate from execution. A capability can be listed without being runnable, and the runtime only executes allowlisted patterns.

## Failure and decision

A fresh installation selected MCP SDK 2.x through the earlier unbounded dependency. Handler unit tests passed, but the new integration test could not start the server because the old FastMCP import no longer existed.

The repair adopted the SDK's MCPServer interface and bounded the dependency to the tested major version. The client test was also updated to SDK 2's response fields. This avoided a compatibility shim around an interface the project no longer tested.

See the [source change](https://github.com/stefan-mcf/automation-kit/commit/3ca13269ce33d77a8149289a626e3a8483bc8013), [dependency contract](../pyproject.toml) and [transport test](../tests/test_mcp_transport.py).

## Verification and review

The transport test starts the real server in a subprocess, initializes a client, discovers tools, reads health, executes an allowed fixture and verifies rejection of a non-enabled pattern. It provides different coverage from directly calling a Python handler.

At the repair revision, local checks reported 153 passing tests, clean Ruff and mypy checks, seven valid patterns and a valid MCP registry. The [CI run for the revision](https://github.com/stefan-mcf/automation-kit/actions?query=sha%3A3ca13269ce33d77a8149289a626e3a8483bc8013) verifies the saved source.

A separate automated Codex review of the frozen diff returned no actionable findings. It was an AI review, not an external human review.

## Reusable skill and harness design

A reusable workflow needs a contract that survives a change of model or agent:

| Element | Concrete contract in this example |
| --- | --- |
| Trigger | A registered tool interface needs protocol-level verification |
| Context | Exact server, dependency, fixture and test paths |
| Tool boundary | Local fixture execution; no account or cloud mutations |
| Handoff | One scoped diff plus check results at a named revision |
| Failure path | Reproduce the boundary failure before changing the interface |
| Completion | Native checks, review and saved GitHub/CI readback |

Specialized skills can carry this contract without loading an entire project's history into every task. Where multiple agents are used, each needs explicit file ownership and a handoff format; this particular change did not require parallel implementation agents.

Development-agent coordination and the application's MCP runtime are separate layers. The former controls how a change is built and checked; the latter exposes the bounded tools implemented by the project.
