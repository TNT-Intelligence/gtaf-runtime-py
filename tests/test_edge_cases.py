import unittest
from datetime import datetime, timezone

from gtaf_runtime import evaluate

UTC = timezone.utc


def _fixture() -> tuple[dict, dict, dict, datetime]:
    now = datetime(2026, 2, 8, 12, 0, tzinfo=UTC)
    drc = {
        "id": "DRC-003",
        "revision": 3,
        "result": "PERMITTED",
        "gtaf_ref": {"version": "0.1"},
        "scope": "ml.prod",
        "valid_from": "2026-01-01T00:00:00Z",
        "valid_until": "2026-12-31T00:00:00Z",
        "refs": {"sb": ["SB-003"], "dr": ["DR-0003"], "rb": ["RB-003"]},
    }
    artifacts = {
        "SB-003": {
            "scope": "ml.prod",
            "included_components": ["ml.agent"],
            "excluded_components": [],
            "allowed_interfaces": ["ml-api"],
            "valid_from": "2026-01-01T00:00:00Z",
            "valid_until": "2026-12-31T00:00:00Z",
        },
        "DR-0003": {
            "scope": "ml.prod",
            "decisions": ["run_inference"],
            "delegation_mode": "AUTONOMOUS",
            "valid_from": "2026-01-01T00:00:00Z",
            "valid_until": "2026-12-31T00:00:00Z",
        },
        "RB-003": {
            "scope": "ml.prod",
            "active": True,
            "valid_from": "2026-01-01T00:00:00Z",
            "valid_until": "2026-12-31T00:00:00Z",
        },
    }
    context = {
        "scope": "ml.prod",
        "component": "ml.agent",
        "interface": "ml-api",
        "action": "run_inference",
    }
    return drc, artifacts, context, now


class EdgeCaseTests(unittest.TestCase):
    def test_rule_order_unsupported_version_before_other_checks(self) -> None:
        drc, artifacts, context, now = _fixture()
        drc["gtaf_ref"]["version"] = "9.9"
        del artifacts["DR-0003"]

        result = evaluate(drc, context, artifacts, now=now)

        self.assertEqual(result.outcome, "DENY")
        self.assertEqual(result.reason_code, "UNSUPPORTED_GTAF_VERSION")

    def test_rule_order_not_permitted_before_missing_reference(self) -> None:
        drc, artifacts, context, now = _fixture()
        drc["result"] = "NOT_PERMITTED"
        del artifacts["RB-003"]

        result = evaluate(drc, context, artifacts, now=now)

        self.assertEqual(result.outcome, "DENY")
        self.assertEqual(result.reason_code, "DRC_NOT_PERMITTED")

    def test_expired_window_denies(self) -> None:
        drc, artifacts, context, now = _fixture()
        drc["valid_until"] = "2026-02-01T00:00:00Z"

        result = evaluate(drc, context, artifacts, now=now)

        self.assertEqual(result.outcome, "DENY")
        self.assertEqual(result.reason_code, "EXPIRED")

    def test_invalid_drc_schema_denies(self) -> None:
        drc, artifacts, context, now = _fixture()
        drc.pop("id")

        result = evaluate(drc, context, artifacts, now=now)

        self.assertEqual(result.outcome, "DENY")
        self.assertEqual(result.reason_code, "INVALID_DRC_SCHEMA")


if __name__ == "__main__":
    unittest.main()
