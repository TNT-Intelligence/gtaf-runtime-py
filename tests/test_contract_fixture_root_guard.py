from pathlib import Path
import unittest


class ContractFixtureRootGuardTests(unittest.TestCase):
    def test_legacy_projection_fixture_root_does_not_exist(self) -> None:
        legacy_root = Path(__file__).parent / "fixtures" / "projection_v0_1"
        self.assertFalse(legacy_root.exists())


if __name__ == "__main__":
    unittest.main()
