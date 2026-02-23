# Projection Contract Versioning Policy

## Scope

This policy applies to the runtime projection contract consumed by `enforce()` in this repository.
It is developer-facing and implementation-derived for Projection v0.1.

## Projection v0.1 Contract Surface

- Projection v0.1 is the stable runtime contract surface.
- The contract surface is the read-surface documented in `SPEC.md` (fields read from `drc`, `context`, `sb`, `dr`, `rb`).
- Runtime behavior is deterministic first-failure evaluation: the first failing rule defines the deny result.

## Stability Guarantees (v0.1)

Within the v0.x line, unless otherwise documented:

- first-failure model is stable,
- evaluation order is stable,
- existing `reason_code` meanings are stable,
- read-surface semantics for Projection v0.1 are stable.

## Version Binding Rule

- `drc.gtaf_ref.version` is the runtime binding input.
- Runtime accepts a request only if `drc.gtaf_ref.version` is in `supported_versions`.
- Default runtime configuration is `supported_versions = {"0.1"}`.
- If version is not supported, runtime returns `UNSUPPORTED_GTAF_VERSION`.

## Compatibility Classification

Breaking changes (major contract bump) include:

- changing first-failure behavior,
- changing evaluation order,
- removing/renaming/redefining existing `reason_code` semantics,
- changing read-surface field requirements or interpretation,
- schema changes that invalidate previously valid Projection v0.1 payloads.

Non-breaking changes include:

- editorial documentation clarifications,
- additive data that remains ignored by runtime core because it is outside the read-surface,
- additive tests/fixtures that do not change existing expected outcomes.

## Deprecation Policy (Fields and Reason Codes)

- In v0.1, fields and `reason_code` semantics are not silently repurposed.
- Deprecation must be documented before removal or semantic reassignment.
- Removal or semantic reassignment of existing read-surface fields or `reason_code` meanings is breaking.

## Supported Versions (Current)

- Current default supported projection versions: `{"0.1"}`.
- Multiple supported versions are possible only when explicitly passed via `supported_versions`.
