import json
import unittest
from datetime import datetime
from pathlib import Path
from typing import Any

from gtaf_runtime import enforce

try:
    from tests._fixture_paths import CONTRACT_FIXTURE_ROOT
except ModuleNotFoundError:
    from _fixture_paths import CONTRACT_FIXTURE_ROOT

FIXTURE_ROOT = CONTRACT_FIXTURE_ROOT
SCHEMA_ROOT = Path(__file__).parent.parent / "schemas"
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

EXPECTED_SCHEMA_VALIDITY = {
    "happy_execute": True,
    "deny_missing_reference": True,
    "deny_expired_valid_until": True,
    "deny_scope_leak": True,
    "deny_outside_sb": True,
    "deny_dr_mismatch": True,
    "deny_rb_required_missing": True,
    "deny_unsupported_version": False,
    "deny_invalid_drc_structure": False,
}


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _parse_utc(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _is_type(value: Any, expected_type: str) -> bool:
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return (isinstance(value, int) or isinstance(value, float)) and not isinstance(value, bool)
    if expected_type == "boolean":
        return isinstance(value, bool)
    return True


def _validate_date_time(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def _validate_schema(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []

    expected_type = schema.get("type")
    if expected_type is not None and not _is_type(instance, expected_type):
        errors.append(f"{path}: expected type {expected_type}")
        return errors

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: value {instance!r} != const {schema['const']!r}")

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: value {instance!r} not in enum {schema['enum']!r}")

    if isinstance(instance, str):
        min_length = schema.get("minLength")
        if isinstance(min_length, int) and len(instance) < min_length:
            errors.append(f"{path}: string shorter than minLength {min_length}")
        if schema.get("format") == "date-time" and not _validate_date_time(instance):
            errors.append(f"{path}: invalid date-time format")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        minimum = schema.get("minimum")
        if isinstance(minimum, (int, float)) and instance < minimum:
            errors.append(f"{path}: value {instance!r} below minimum {minimum}")

    if isinstance(instance, list):
        min_items = schema.get("minItems")
        if isinstance(min_items, int) and len(instance) < min_items:
            errors.append(f"{path}: array has fewer than minItems {min_items}")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for idx, item in enumerate(instance):
                errors.extend(_validate_schema(item, item_schema, f"{path}[{idx}]"))

    if isinstance(instance, dict):
        required = schema.get("required", [])
        if isinstance(required, list):
            for key in required:
                if key not in instance:
                    errors.append(f"{path}: missing required property {key!r}")

        properties = schema.get("properties", {})
        if isinstance(properties, dict):
            for key, prop_schema in properties.items():
                if key in instance and isinstance(prop_schema, dict):
                    errors.extend(_validate_schema(instance[key], prop_schema, f"{path}.{key}"))

    return errors


class ProjectionV01ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.drc_schema = _load_json(SCHEMA_ROOT / "drc.schema.json")
        cls.context_schema = _load_json(SCHEMA_ROOT / "runtime_context.schema.json")
        cls.sb_schema = _load_json(SCHEMA_ROOT / "sb.schema.json")
        cls.dr_schema = _load_json(SCHEMA_ROOT / "dr.schema.json")
        cls.rb_schema = _load_json(SCHEMA_ROOT / "rb.schema.json")

    def _load_case(self, case_name: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
        case_dir = FIXTURE_ROOT / case_name
        drc = _load_json(case_dir / "drc.json")
        artifacts = _load_json(case_dir / "artifacts.json")
        context = _load_json(case_dir / "context.json")
        expected = _load_json(case_dir / "expected.json")
        return drc, artifacts, context, expected

    def test_fixture_schema_alignment_matrix(self) -> None:
        for case_name in CASE_DIRS:
            with self.subTest(case=case_name):
                drc, artifacts, context, _ = self._load_case(case_name)

                drc_errors = _validate_schema(drc, self.drc_schema, "$.drc")
                context_errors = _validate_schema(context, self.context_schema, "$.context")
                artifact_errors: list[str] = []

                refs = drc.get("refs", {}) if isinstance(drc, dict) else {}

                for ref_id in refs.get("sb", []) if isinstance(refs, dict) else []:
                    if ref_id in artifacts:
                        artifact_errors.extend(
                            _validate_schema(artifacts[ref_id], self.sb_schema, f"$.artifacts[{ref_id!r}]")
                        )

                for ref_id in refs.get("dr", []) if isinstance(refs, dict) else []:
                    if ref_id in artifacts:
                        artifact_errors.extend(
                            _validate_schema(artifacts[ref_id], self.dr_schema, f"$.artifacts[{ref_id!r}]")
                        )

                for ref_id in refs.get("rb", []) if isinstance(refs, dict) else []:
                    if ref_id in artifacts:
                        artifact_errors.extend(
                            _validate_schema(artifacts[ref_id], self.rb_schema, f"$.artifacts[{ref_id!r}]")
                        )

                all_errors = [*drc_errors, *context_errors, *artifact_errors]
                is_schema_valid = len(all_errors) == 0
                self.assertEqual(
                    is_schema_valid,
                    EXPECTED_SCHEMA_VALIDITY[case_name],
                    msg=f"Schema validity mismatch for {case_name}: {all_errors}",
                )

                if case_name == "deny_unsupported_version":
                    self.assertTrue(
                        any("gtaf_ref.version" in e and "const '0.1'" in e for e in drc_errors),
                        msg=f"Expected const-version schema failure for {case_name}, got: {drc_errors}",
                    )

                if case_name == "deny_invalid_drc_structure":
                    self.assertTrue(
                        any("missing required property 'id'" in e for e in drc_errors),
                        msg=f"Expected missing-id schema failure for {case_name}, got: {drc_errors}",
                    )

    def test_contract_enforcement_matrix(self) -> None:
        for case_name in CASE_DIRS:
            with self.subTest(case=case_name):
                drc, artifacts, context, expected = self._load_case(case_name)

                result = enforce(drc, context, artifacts, now=_parse_utc(expected["now"]))

                self.assertEqual(result.outcome, expected["outcome"])
                self.assertEqual(result.reason_code, expected["reason_code"])

    def test_first_failure_precedence_unsupported_version_over_missing_reference(self) -> None:
        drc, artifacts, context, expected = self._load_case("happy_execute")

        drc["gtaf_ref"]["version"] = "0.2"
        del artifacts["DR-FX-001"]

        result = enforce(drc, context, artifacts, now=_parse_utc(expected["now"]))

        self.assertEqual(result.outcome, "DENY")
        self.assertEqual(result.reason_code, "UNSUPPORTED_GTAF_VERSION")

    def test_first_failure_precedence_not_permitted_over_missing_reference(self) -> None:
        drc, artifacts, context, expected = self._load_case("happy_execute")

        drc["result"] = "NOT_PERMITTED"
        del artifacts["DR-FX-001"]

        result = enforce(drc, context, artifacts, now=_parse_utc(expected["now"]))

        self.assertEqual(result.outcome, "DENY")
        self.assertEqual(result.reason_code, "DRC_NOT_PERMITTED")


if __name__ == "__main__":
    unittest.main()
