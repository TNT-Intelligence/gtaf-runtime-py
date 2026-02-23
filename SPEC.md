# GTAF Runtime Specification

## Projection Contract

### Projection v0.1

Projection v0.1 reflects the current `enforce()` implementation and does not redefine normative GTAF artifacts. It documents only fields actually read by the runtime core.

#### `drc`

| field path | access mode | required vs conditional | runtime implication |
|---|---|---|---|
| `id` | direct | required | must exist and be non-empty string in DRC validation; echoed in result payload |
| `revision` | direct | required | must exist and be integer `>= 1` in DRC validation; echoed in result payload |
| `result` | direct | required | must exist; validated as `PERMITTED` or `NOT_PERMITTED`; only `PERMITTED` continues |
| `gtaf_ref` | direct | required | must exist as object |
| `gtaf_ref.version` | direct | required | must exist as non-empty string; must be in `supported_versions` |
| `scope` | direct | required | must exist as non-empty string; must equal `context.scope` |
| `valid_from` | `.get()` | conditionally required | parsed as datetime; missing/unparseable causes denial |
| `valid_until` | `.get()` | conditionally required | parsed as datetime; missing/unparseable causes denial; echoed in result payload |
| `refs` | direct | required | must exist as object |
| `refs.sb` | direct | required | must exist as list of non-empty strings; minimum length 1 |
| `refs.dr` | direct | required | must exist as list of non-empty strings; minimum length 1 |
| `refs.rb` | direct | required | must exist as list of non-empty strings; may be empty |

#### `context`

| field path | access mode | required vs conditional | runtime implication |
|---|---|---|---|
| `scope` | `.get()` | conditionally required | must be non-empty string and equal `drc.scope` |
| `component` | `.get()` | conditionally required | must be string; must be included by SB and not excluded |
| `interface` | `.get()` | conditionally required | must be string; must be in SB `allowed_interfaces` |
| `action` | `.get()` | conditionally required | must be string; must match a DR `decisions` entry |

#### `sb` (resolved from `drc.refs.sb`)

| field path | access mode | required vs conditional | runtime implication |
|---|---|---|---|
| `valid_from` | `.get()` | conditionally required | parsed as datetime for artifact window check |
| `valid_until` | `.get()` | conditionally required | parsed as datetime for artifact window check |
| `scope` | `.get()` | conditionally required | must equal `context.scope` or be covered by `linked_scopes` |
| `linked_scopes` | `.get()` | conditionally required | optional alternate scope match list |
| `included_components` | `.get()` | conditionally required | `context.component` must be present |
| `excluded_components` | `.get()` | conditionally required | `context.component` must not be present |
| `allowed_interfaces` | `.get()` | conditionally required | `context.interface` must be present |

#### `dr` (resolved from `drc.refs.dr`)

| field path | access mode | required vs conditional | runtime implication |
|---|---|---|---|
| `valid_from` | `.get()` | conditionally required | parsed as datetime for artifact window check |
| `valid_until` | `.get()` | conditionally required | parsed as datetime for artifact window check |
| `scope` | `.get()` | conditionally required | must equal `context.scope` or be covered by `linked_scopes` |
| `linked_scopes` | `.get()` | conditionally required | optional alternate scope match list |
| `decisions` | `.get()` | conditionally required | expected list; must contain `context.action` in at least one DR |
| `delegation_mode` | `.get()` | conditionally required | if `SEMI_AUTONOMOUS` or `AUTONOMOUS`, at least one truthy RB `active` is required |

#### `rb` (resolved from `drc.refs.rb`)

| field path | access mode | required vs conditional | runtime implication |
|---|---|---|---|
| `valid_from` | `.get()` | conditionally required | parsed as datetime for artifact window check |
| `valid_until` | `.get()` | conditionally required | parsed as datetime for artifact window check |
| `scope` | `.get()` | conditionally required | must equal `context.scope` or be covered by `linked_scopes` |
| `linked_scopes` | `.get()` | conditionally required | optional alternate scope match list |
| `active` | `.get()` | conditionally required | interpreted by truthiness (`bool(rb.get("active"))`) |

### Core Read Surface and Validation Status (v0.1)

- Projection v0.1 is the stable runtime contract surface for `enforce()`: only the field paths listed above are read by the core decision logic.
- The runtime consumes a projection payload (`drc`, `context`, resolved `sb`/`dr`/`rb`) and does not consume full normative GTAF artifact models.
- Unknown or extra fields in `drc`, `context`, and artifacts are ignored unless they overlap with a field path read by the core.
- `schemas/` define Projection v0.1 validation artifacts; they can be used upstream to validate projection payloads before runtime execution.
- Current runtime check status (implementation-derived): `drc` structure is checked by `_validate_drc_schema`; `context`, `sb`, `dr`, and `rb` are not JSON-schema-validated by the runtime before rule checks.

## Known Runtime Implicit Assumptions (v0.1)

- Datetimes are parsed via `datetime.fromisoformat` after replacing `Z` with `+00:00`.
- Validity windows are evaluated as `valid_from <= now < valid_until` (end exclusive).
- `context` and resolved artifacts are not schema-validated before rule checks.
- Scope coherence accepts either direct `scope` equality or membership in `linked_scopes`.
- For boundary checks, only `sb_items[0]` is evaluated.
- For DR action matching, the first matching DR in iteration order is used.
- `rb.active` is evaluated via truthiness, not strict boolean type checking.

## Version History

### Projection v0.1
- Initial formalization of runtime projection contract.
- Descriptive specification derived from enforce() implementation.
- No enforcement semantics modified.
