from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from . import errors
from .types import EnforcementResult

PROJECTION_CONTRACT_VERSION = "0.1"

def evaluate(
    drc: dict[str, Any],
    context: dict[str, Any],
    artifacts: dict[str, dict[str, Any]],
    *,
    supported_versions: set[str] | None = None,
    now: datetime | None = None,
) -> EnforcementResult:
    """
    Deterministic GTAF-3 runtime gate.
    Returns EXECUTE only if all checks pass; otherwise DENY with the first failing reason.
    """
    supported_versions = supported_versions or {"0.1"}
    ts = now or datetime.now(UTC)

    try:
        return _evaluate_inner(
            drc=drc,
            context=context,
            artifacts=artifacts,
            supported_versions=supported_versions,
            now=ts,
        )
    except Exception:
        return _deny(drc, errors.INTERNAL_ERROR, refs=_refs_from_drc(drc))


def _evaluate_inner(
    *,
    drc: dict[str, Any],
    context: dict[str, Any],
    artifacts: dict[str, dict[str, Any]],
    supported_versions: set[str],
    now: datetime,
) -> EnforcementResult:
    # 1) Parse & validate DRC instance.
    if not _validate_drc_schema(drc):
        return _deny(drc, errors.INVALID_DRC_SCHEMA, refs=_refs_from_drc(drc))

    drc_refs = _refs_from_drc(drc)

    # 2) Reference version binding.
    version = drc["gtaf_ref"]["version"]
    if version not in supported_versions:
        return _deny(drc, errors.UNSUPPORTED_GTAF_VERSION, refs=drc_refs)

    # 3) Temporality for DRC itself.
    if not _within_window(drc.get("valid_from"), drc.get("valid_until"), now):
        return _deny(drc, errors.EXPIRED, refs=drc_refs)

    # 4) Binary gate.
    if drc["result"] != "PERMITTED":
        return _deny(drc, errors.DRC_NOT_PERMITTED, refs=drc_refs)

    # 5) Referential closure + temporal validity of referenced artifacts.
    sb_items = _resolve_refs(drc["refs"]["sb"], artifacts)
    dr_items = _resolve_refs(drc["refs"]["dr"], artifacts)
    rb_items = _resolve_refs(drc["refs"]["rb"], artifacts)
    if sb_items is None or dr_items is None or rb_items is None:
        return _deny(drc, errors.MISSING_REFERENCE, refs=drc_refs)

    for item in [*sb_items, *dr_items, *rb_items]:
        if not _within_window(item.get("valid_from"), item.get("valid_until"), now):
            return _deny(drc, errors.EXPIRED, refs=drc_refs)

    # 6) Scope coherence.
    ctx_scope = context.get("scope")
    if not isinstance(ctx_scope, str) or not ctx_scope:
        return _deny(drc, errors.SCOPE_LEAK, refs=drc_refs)
    if ctx_scope != drc["scope"]:
        return _deny(drc, errors.SCOPE_LEAK, refs=drc_refs)
    for item in [*sb_items, *dr_items, *rb_items]:
        if not _scope_matches(ctx_scope, item):
            return _deny(drc, errors.SCOPE_LEAK, refs=drc_refs)

    # 7) SB scope check.
    component = context.get("component")
    interface = context.get("interface")
    if not _inside_system_boundary(sb_items[0], component=component, interface=interface):
        return _deny(drc, errors.OUTSIDE_SB, refs=drc_refs)

    # 8) DR action identity check.
    action = context.get("action")
    matched_dr = _match_decision_record(dr_items, action)
    if matched_dr is None:
        return _deny(drc, errors.DR_MISMATCH, refs=drc_refs)

    # 9) RB presence rule for semi/autonomous execution.
    mode = matched_dr.get("delegation_mode")
    if mode in {"SEMI_AUTONOMOUS", "AUTONOMOUS"}:
        active_rb = any(bool(rb.get("active")) for rb in rb_items)
        if not active_rb:
            return _deny(drc, errors.RB_REQUIRED, refs=drc_refs)

    return EnforcementResult(
        outcome="EXECUTE",
        drc_id=drc.get("id"),
        revision=drc.get("revision"),
        valid_until=drc.get("valid_until"),
        reason_code="OK",
        refs=drc_refs,
        details={},
    )


def _resolve_refs(ids: list[str], artifacts: dict[str, dict[str, Any]]) -> list[dict[str, Any]] | None:
    resolved: list[dict[str, Any]] = []
    for ref_id in ids:
        item = artifacts.get(ref_id)
        if item is None:
            return None
        resolved.append(item)
    return resolved


def _scope_matches(scope: str, artifact: dict[str, Any]) -> bool:
    artifact_scope = artifact.get("scope")
    if artifact_scope == scope:
        return True
    linked = artifact.get("linked_scopes", [])
    return isinstance(linked, list) and scope in linked


def _inside_system_boundary(sb: dict[str, Any], *, component: Any, interface: Any) -> bool:
    included = sb.get("included_components", [])
    excluded = sb.get("excluded_components", [])
    allowed_if = sb.get("allowed_interfaces", [])

    if not isinstance(component, str) or component not in included or component in excluded:
        return False
    if not isinstance(interface, str) or interface not in allowed_if:
        return False
    return True


def _match_decision_record(dr_items: list[dict[str, Any]], action: Any) -> dict[str, Any] | None:
    if not isinstance(action, str):
        return None
    for dr in dr_items:
        decisions = dr.get("decisions", [])
        if isinstance(decisions, list) and action in decisions:
            return dr
    return None


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    parsed = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(parsed)
    except ValueError:
        return None


def _within_window(valid_from: Any, valid_until: Any, now: datetime) -> bool:
    start = _parse_datetime(valid_from)
    end = _parse_datetime(valid_until)
    if start is None or end is None:
        return False
    return start <= now < end


def _refs_from_drc(drc: dict[str, Any]) -> list[str]:
    refs = drc.get("refs")
    if not isinstance(refs, dict):
        return []
    values: list[str] = []
    for key in ("sb", "dr", "rb"):
        items = refs.get(key, [])
        if isinstance(items, list):
            values.extend([item for item in items if isinstance(item, str)])
    return values


def _deny(drc: dict[str, Any], reason_code: str, *, refs: list[str]) -> EnforcementResult:
    return EnforcementResult(
        outcome="DENY",
        drc_id=drc.get("id") if isinstance(drc, dict) else None,
        revision=drc.get("revision") if isinstance(drc, dict) else None,
        valid_until=drc.get("valid_until") if isinstance(drc, dict) else None,
        reason_code=reason_code,
        refs=refs,
        details={},
    )


def _validate_drc_schema(drc: dict[str, Any]) -> bool:
    if not isinstance(drc, dict):
        return False

    required = {
        "id",
        "revision",
        "result",
        "gtaf_ref",
        "scope",
        "valid_from",
        "valid_until",
        "refs",
    }
    if any(key not in drc for key in required):
        return False

    if not isinstance(drc.get("id"), str) or not drc["id"]:
        return False
    if not isinstance(drc.get("revision"), int) or drc["revision"] < 1:
        return False
    if drc.get("result") not in {"PERMITTED", "NOT_PERMITTED"}:
        return False
    if not isinstance(drc.get("scope"), str) or not drc["scope"]:
        return False
    if _parse_datetime(drc.get("valid_from")) is None:
        return False
    if _parse_datetime(drc.get("valid_until")) is None:
        return False

    gtaf_ref = drc.get("gtaf_ref")
    if not isinstance(gtaf_ref, dict):
        return False
    if not isinstance(gtaf_ref.get("version"), str) or not gtaf_ref["version"]:
        return False

    refs = drc.get("refs")
    if not isinstance(refs, dict):
        return False
    for required_ref in ("sb", "dr", "rb"):
        if required_ref not in refs:
            return False
        if not isinstance(refs[required_ref], list):
            return False
    if len(refs["sb"]) < 1 or len(refs["dr"]) < 1:
        return False
    for group in ("sb", "dr", "rb"):
        if not all(isinstance(item, str) and item for item in refs[group]):
            return False

    return True
