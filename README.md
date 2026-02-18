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
- `schemas/`: schema placeholders / artifacts for future interoperability alignment

## License
See `LICENSE`.
