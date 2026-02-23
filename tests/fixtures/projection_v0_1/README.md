# Projection v0.1 Runtime Fixtures

Deterministic fixtures for runtime contract testing.

Each case directory contains:
- `drc.json`
- `artifacts.json`
- `context.json`
- `expected.json`

`expected.json` defines:
- `outcome`
- `reason_code`
- `now` (fixed evaluation timestamp in UTC)

Cases included (exactly):
- `happy_execute`
- `deny_missing_reference`
- `deny_expired_valid_until`
- `deny_scope_leak`
- `deny_outside_sb`
- `deny_dr_mismatch`
- `deny_rb_required_missing`
- `deny_unsupported_version`
- `deny_invalid_drc_structure`

## Contract intent (v0.1 fixtures)

- These fixtures freeze the effective Projection v0.1 runtime behavior.
- Projection v0.1 follows a strict first-failure model.
- The evaluation order in `enforce()` defines canonical outcomes.
- `refs` list ordering (`sb` / `dr` / `rb`) is semantically significant in v0.1.
- Any change to evaluation order or reason-code semantics is a breaking change of the Projection v0.1 contract.
