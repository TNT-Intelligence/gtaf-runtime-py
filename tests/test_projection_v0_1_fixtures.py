import json
import unittest
from datetime import datetime
from pathlib import Path

from gtaf_runtime import evaluate


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "projection_v0_1"
CASE_DIRS = [
    "happy_execute",
    "deny_missing_reference",
    "deny_expired_valid_until",
    "deny_scope_leak",
    "deny_outside_sb",
    "deny_dr_mismatch",
    "deny_rb_required_missing",
    "deny_unsupported_version",
    "deny_invalid_drc_structure",
]


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _parse_utc(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


class ProjectionV01FixtureTests(unittest.TestCase):
    def test_projection_v01_fixture_matrix(self) -> None:
        for case_name in CASE_DIRS:
            case_dir = FIXTURE_ROOT / case_name
            with self.subTest(case=case_name):
                drc = _load_json(case_dir / "drc.json")
                artifacts = _load_json(case_dir / "artifacts.json")
                context = _load_json(case_dir / "context.json")
                expected = _load_json(case_dir / "expected.json")

                result = evaluate(drc, context, artifacts, now=_parse_utc(expected["now"]))

                self.assertEqual(result.outcome, expected["outcome"])
                self.assertEqual(result.reason_code, expected["reason_code"])


if __name__ == "__main__":
    unittest.main()
