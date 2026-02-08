import unittest
from datetime import UTC, datetime

from gtaf_runtime import evaluate


def _base() -> tuple[dict, dict, dict, datetime]:
    now = datetime(2026, 2, 8, 12, 0, tzinfo=UTC)
    drc = {
        "id": "DRC-002",
        "revision": 1,
        "result": "PERMITTED",
        "gtaf_ref": {"version": "0.1"},
        "scope": "ops.prod",
        "valid_from": "2026-01-01T00:00:00Z",
        "valid_until": "2026-12-31T00:00:00Z",
        "refs": {"sb": ["SB-002"], "dr": ["DR-0002"], "rb": ["RB-002"]},
    }
    artifacts = {
        "SB-002": {
            "scope": "ops.prod",
            "included_components": ["ops.agent"],
            "excluded_components": [],
            "allowed_interfaces": ["ops-api"],
            "valid_from": "2026-01-01T00:00:00Z",
            "valid_until": "2026-12-31T00:00:00Z",
        },
        "DR-0002": {
            "scope": "ops.prod",
            "decisions": ["restart_worker"],
            "delegation_mode": "AUTONOMOUS",
            "valid_from": "2026-01-01T00:00:00Z",
            "valid_until": "2026-12-31T00:00:00Z",
        },
        "RB-002": {
            "scope": "ops.prod",
            "active": True,
            "valid_from": "2026-01-01T00:00:00Z",
            "valid_until": "2026-12-31T00:00:00Z",
        },
    }
    context = {
        "scope": "ops.prod",
        "component": "ops.agent",
        "interface": "ops-api",
        "action": "restart_worker",
    }
    return drc, artifacts, context, now


class DenyTests(unittest.TestCase):
    def test_deny_if_drc_not_permitted(self) -> None:
        drc, artifacts, context, now = _base()
        drc["result"] = "NOT_PERMITTED"

        result = evaluate(drc, context, artifacts, now=now)

        self.assertEqual(result.outcome, "DENY")
        self.assertEqual(result.reason_code, "DRC_NOT_PERMITTED")

    def test_deny_if_reference_missing(self) -> None:
        drc, artifacts, context, now = _base()
        del artifacts["DR-0002"]

        result = evaluate(drc, context, artifacts, now=now)

        self.assertEqual(result.outcome, "DENY")
        self.assertEqual(result.reason_code, "MISSING_REFERENCE")

    def test_deny_if_outside_system_boundary(self) -> None:
        drc, artifacts, context, now = _base()
        context["component"] = "outside.component"

        result = evaluate(drc, context, artifacts, now=now)

        self.assertEqual(result.outcome, "DENY")
        self.assertEqual(result.reason_code, "OUTSIDE_SB")

    def test_deny_if_action_not_in_decision_record(self) -> None:
        drc, artifacts, context, now = _base()
        context["action"] = "delete_cluster"

        result = evaluate(drc, context, artifacts, now=now)

        self.assertEqual(result.outcome, "DENY")
        self.assertEqual(result.reason_code, "DR_MISMATCH")

    def test_deny_if_rb_required_but_not_active(self) -> None:
        drc, artifacts, context, now = _base()
        artifacts["RB-002"]["active"] = False

        result = evaluate(drc, context, artifacts, now=now)

        self.assertEqual(result.outcome, "DENY")
        self.assertEqual(result.reason_code, "RB_REQUIRED")


if __name__ == "__main__":
    unittest.main()
