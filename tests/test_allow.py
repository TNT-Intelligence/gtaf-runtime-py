import unittest
from datetime import UTC, datetime

from gtaf_runtime import evaluate


class AllowTests(unittest.TestCase):
    def test_execute_when_all_checks_pass(self) -> None:
        now = datetime(2026, 2, 8, 12, 0, tzinfo=UTC)
        drc = {
            "id": "DRC-001",
            "revision": 1,
            "result": "PERMITTED",
            "gtaf_ref": {"version": "0.1"},
            "scope": "payments.prod",
            "valid_from": "2026-02-01T00:00:00Z",
            "valid_until": "2026-03-01T00:00:00Z",
            "refs": {"sb": ["SB-001"], "dr": ["DR-0001"], "rb": ["RB-001"]},
        }
        artifacts = {
            "SB-001": {
                "scope": "payments.prod",
                "included_components": ["agent.runtime"],
                "excluded_components": [],
                "allowed_interfaces": ["payments-api"],
                "valid_from": "2026-01-01T00:00:00Z",
                "valid_until": "2026-12-31T00:00:00Z",
            },
            "DR-0001": {
                "scope": "payments.prod",
                "decisions": ["approve_refund"],
                "delegation_mode": "AUTONOMOUS",
                "valid_from": "2026-01-01T00:00:00Z",
                "valid_until": "2026-12-31T00:00:00Z",
            },
            "RB-001": {
                "scope": "payments.prod",
                "active": True,
                "valid_from": "2026-01-01T00:00:00Z",
                "valid_until": "2026-12-31T00:00:00Z",
            },
        }
        context = {
            "scope": "payments.prod",
            "component": "agent.runtime",
            "interface": "payments-api",
            "action": "approve_refund",
        }

        result = evaluate(drc, context, artifacts, now=now)

        self.assertEqual(result.outcome, "EXECUTE")
        self.assertEqual(result.reason_code, "OK")


if __name__ == "__main__":
    unittest.main()
