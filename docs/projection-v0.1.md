# Projection v0.1 Runtime Contract (Normative)

## 1. Scope and Layer Separation

This document defines the **Projection v0.1 runtime contract** for `gtaf-runtime-py`.

Projection v0.1 SHALL define deterministic runtime evaluation semantics for `enforce()` / `evaluate()` inputs and outputs.

Projection v0.1 SHALL be treated as a separate layer from:
- the GTAF conceptual reference model,
- the runtime implementation internals,
- SDK integration helpers.

Projection v0.1 SHALL govern only the runtime contract surface exercised by `enforce()`.

## 2. Normative Semantics Model

### 2.1 First-Failure Rule (MUST)

Evaluation MUST follow a strict first-failure model.

Runtime evaluation MUST stop at the first failing condition.

### 2.2 EXECUTE Preconditions (MUST)

`EXECUTE` SHALL be returned only if all checks pass.

If any check fails, runtime SHALL return `DENY`.

### 2.3 No Override Rule (MUST NOT)

A later condition MUST NOT override an earlier failure.

## 3. Canonical Evaluation Order (Frozen for v0.1)

Projection v0.1 evaluation order SHALL be exactly:

1. `INVALID_DRC_SCHEMA`
2. `UNSUPPORTED_GTAF_VERSION`
3. DRC validity window check -> `EXPIRED`
4. DRC binary gate -> `DRC_NOT_PERMITTED`
5. Reference resolution -> `MISSING_REFERENCE`
6. Referenced artifact validity window check -> `EXPIRED`
7. Scope coherence -> `SCOPE_LEAK`
8. System boundary check -> `OUTSIDE_SB`
9. DR action match -> `DR_MISMATCH`
10. RB requirement for `SEMI_AUTONOMOUS` / `AUTONOMOUS` -> `RB_REQUIRED`
11. Success outcome -> `EXECUTE` with `reason_code="OK"`

### 3.1 INTERNAL_ERROR Fallback

If an unexpected exception is raised during evaluation, runtime SHALL return:
- `outcome="DENY"`
- `reason_code="INTERNAL_ERROR"`

This fallback SHALL remain part of the Projection v0.1 contract surface.

## 4. Ordering Sensitivity (Normative)

### 4.1 `drc.refs.dr` Ordering

`drc.refs.dr` ordering SHALL be preserved during resolution.

DR matching SHALL iterate in that order.

The first DR whose `decisions` contains `context.action` SHALL be authoritative for `delegation_mode` used by the RB requirement check.

### 4.2 `drc.refs.sb` Ordering

`drc.refs.sb` ordering SHALL be preserved during resolution.

System boundary evaluation SHALL use only the first SB referenced in `drc.refs.sb` after successful resolution.

### 4.3 `drc.refs.rb` Ordering

`drc.refs.rb` ordering SHALL be preserved during resolution and earlier artifact checks.

RB requirement SHALL be satisfied if and only if at least one resolved RB has a truthy `active` value; otherwise runtime SHALL return `RB_REQUIRED` when the matched DR delegation mode is `SEMI_AUTONOMOUS` or `AUTONOMOUS`.

## 5. Reason Code Contract Surface

The following reason codes are part of the Projection v0.1 runtime contract surface:

- `INVALID_DRC_SCHEMA`
- `UNSUPPORTED_GTAF_VERSION`
- `EXPIRED`
- `DRC_NOT_PERMITTED`
- `MISSING_REFERENCE`
- `SCOPE_LEAK`
- `OUTSIDE_SB`
- `DR_MISMATCH`
- `RB_REQUIRED`
- `INTERNAL_ERROR`
- `OK` (success reason code for `EXECUTE`)

Reason code meaning SHALL be stable within Projection v0.1.

Reason code meaning MUST NOT be repurposed within Projection v0.1.

## 6. Breaking Change Criteria (MAJOR)

The following SHALL be treated as breaking changes of the Projection contract surface:

- changing first-failure semantics,
- changing canonical evaluation order,
- changing meaning of any existing reason code,
- changing ordering sensitivity behavior for `refs` evaluation,
- changing binary outcome semantics (`EXECUTE` / `DENY`),
- changing the contract-visible fallback behavior producing `INTERNAL_ERROR`.

## 7. Relationship to Contract Fixtures

`contract_fixtures/v0.1/` SHALL be treated as the executable guard for Projection v0.1.

Contract fixtures and contract tests SHALL provide regression protection for the current frozen runtime contract behavior.

Fixture guarantees in v0.1 SHALL be limited to the current matrix expectations (`outcome`, `reason_code`, deterministic `expected.now` evaluation timestamp).

## 8. Relationship to SPEC and VERSIONING

`SPEC.md` SHALL remain the projection field-surface specification for runtime reads and validation status.

`VERSIONING.md` SHALL remain the versioning and compatibility policy for the projection contract surface.

This document SHALL define normative runtime contract semantics for Projection v0.1 consistent with those files.

## 9. Conformance Statement (v0.1)

An implementation claiming Projection v0.1 conformance SHALL:
- apply the canonical evaluation order exactly,
- preserve strict first-failure behavior,
- preserve ordering sensitivity exactly as defined above,
- produce contract reason codes with unchanged meaning,
- return `EXECUTE` only when all checks pass,
- return `INTERNAL_ERROR` on unexpected evaluation exceptions.
