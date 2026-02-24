# GTAF Runtime (Python)
Official reference implementation of the GTAF Runtime Enforcement core.

This repository is `gtaf-runtime-py`.

`gtaf-runtime` is a **deterministic, artifact-driven enforcement gate** for delegated actions.  
It consumes evaluated governance outputs (for example DRC + referenced artifacts) and returns binary runtime outcomes.

## Status
This repository is the **runtime enforcement implementation**, not the normative reference.  
Current package version: **0.1.0**.

## Scope
This repository contains:
- a minimal enforcement API (`enforce`, with backward-compatible `evaluate` alias)
- deterministic rule evaluation with default-deny behavior
- machine-readable deny reason codes
- tests for allow/deny and rule-order edge cases

## Runtime Specification
The runtime projection contract is formally defined in `SPEC.md`.

Projection v0.1 documents the exact input surface consumed by `enforce()` and reflects the current implementation without redefining normative GTAF artifacts.
The canonical Projection v0.1 contract fixture kit is `contract_fixtures/v0.1/`.
Normative Projection v0.1 runtime contract: `docs/projection-v0.1.md`.

## Runtime Stability & Compatibility

### Stability Level

The current package version is `0.1.x`.

The runtime is considered **alpha with respect to API ergonomics**, but the
**Projection v0.1 semantic contract is frozen**.

This means:

- Enforcement semantics defined in `docs/projection-v0.1.md` are stable.
- Evaluation order, first-failure behavior, and reason code meaning are frozen for Projection v0.1.
- Runtime API ergonomics (e.g., module organization, helper layout) may evolve
  as long as enforcement semantics remain unchanged.


### Projection Contract Freeze (v0.1)

Projection v0.1 defines a deterministic runtime contract.

For Projection version `"0.1"`:

- Canonical evaluation order is frozen.
- First-failure semantics are frozen.
- Ordering sensitivity rules are frozen.
- Reason code meaning is frozen.

Any change to these semantics requires a **MAJOR version increment**
of the Projection contract.


### Supported Projection Versions

The runtime currently supports Projection version:

- `"0.1"`

If a DRC declares an unsupported `gtaf_ref.version`,
`enforce()` SHALL return:

- `outcome="DENY"`
- `reason_code="UNSUPPORTED_GTAF_VERSION"`

Future Projection versions (e.g. `"0.2"`) require explicit runtime support.


### Breaking Changes (MAJOR)

The following changes are considered breaking at the Projection contract level
and require a MAJOR version increment:

- Changing evaluation order.
- Changing first-failure semantics.
- Changing meaning of any existing reason code.
- Changing binary outcome semantics (`EXECUTE` / `DENY`).
- Renaming or removing reason codes.
- Changing ordering sensitivity behavior for `refs` resolution.
- Changing the contract-visible `INTERNAL_ERROR` fallback behavior.


### Non-Breaking Changes

The following are considered non-breaking:

- Internal refactoring.
- Performance improvements.
- Logging improvements.
- Documentation updates.
- CI changes.
- Non-semantic helper utilities.
- Internal module reorganization.


### Public Runtime Contract Surface

The following surface is considered stable and safe for external consumers
(including `gtaf-sdk-py`):

- `gtaf_runtime.enforce(...)`
- `gtaf_runtime.evaluate(...)` (alias of `enforce`)
- The `EnforcementResult` output contract shape
  (including `outcome` and `reason_code`)
- Projection v0.1 semantics as defined in:
  - `docs/projection-v0.1.md`
  - `SPEC.md`
  - `contract_fixtures/v0.1/`
- The supported Projection version policy (currently `"0.1"`)

Structural DRC validation is guaranteed as part of the `enforce()` contract
flow (first evaluation stage), but no separate validation helper function is
considered a stable public API.


### Internal / Non-Contractual Implementation Details

The following are NOT part of the public contract and may change without notice:

- Underscore-prefixed helpers (e.g. `_validate_drc_schema`)
- Internal resolution helpers
- Internal module layout
- Private utilities
- Internal evaluation mechanics

Consumers and SDK MUST NOT rely on internal or underscore-prefixed symbols.


### Relationship to SDK

`gtaf-runtime-py` is the deterministic enforcement core.

`gtaf-sdk-py` is optional and layered on top of the runtime.

The SDK MUST rely only on the documented public runtime contract surface
and MUST NOT depend on internal implementation details.

The SDK MUST NOT alter or reinterpret runtime enforcement semantics.

## JSON Schemas

Projection v0.1 is additionally formalized using JSON Schemas under `gtaf_runtime/schemas/`.

These schemas describe the exact runtime projection surface consumed by `enforce()` and can be used by integrators or SDKs to validate inputs prior to runtime execution.

Packaged schema resources can be accessed via `importlib.resources` from `gtaf_runtime.schemas`.

Schema validation is not performed automatically by the runtime core.

## Non-Goals
`gtaf-runtime` is **not**:
- a governance authoring tool
- a normative GTAF reference publication
- a certification or compliance platform

## Public API
```python
from gtaf_runtime import enforce

result = enforce(drc, context, artifacts)
if result.outcome == "DENY":
    raise PermissionError(result.reason_code)
```

Backward compatibility:
```python
from gtaf_runtime import evaluate  # alias to enforce
```

## Installation
Install from PyPI:
```sh
pip install gtaf-runtime
```

Install from local checkout:
```sh
pip install .
```

Minimal import verification:
```sh
python -c "import gtaf_runtime; from gtaf_runtime import enforce; print('ok')"
```

## Runtime Semantics (Minimal)
- Outcomes: `EXECUTE` or `DENY`
- Decision mode: deterministic, first failing rule wins
- Ambiguity/error handling: deny by default
- Explainability fields: `outcome`, `drc_id`, `revision`, `valid_until`, `reason_code`, `refs`

## Local Development
Run tests:
```sh
python -m unittest discover -s tests -p 'test_*.py' -v
```

## Repository Structure
- `gtaf_runtime/`: runtime library
- `tests/`: enforcement behavior tests
- `gtaf_runtime/schemas/`: packaged Projection v0.1 schema artifacts

## License
See `LICENSE`.
