"""Naming migration gates keep old or interrupted state from live role use."""
import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from role_state import MARKER, status, require_ready
from runtime.storage import SafetyError


class RoleStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="hai-role-state-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def write_marker(self, value):
        path = self.root / MARKER
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_new_environment_needs_no_migration_marker(self):
        self.assertEqual(status(self.root)["status"], "ready")
        require_ready(self.root)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_each_legacy_root_requires_explicit_migration(self):
        for relative in (".hai_env/agents", ".hai_env/config/agents", "hai_agents_library", ".hai/agents"):
            with self.subTest(relative=relative):
                path = self.root / relative
                path.mkdir(parents=True)
                self.assertEqual(status(self.root)["status"], "migration_required")
                with self.assertRaises(SafetyError):
                    require_ready(self.root)
                path.rmdir()

    def test_mixed_or_incomplete_state_is_partial(self):
        (self.root / ".hai_env/agents").mkdir(parents=True)
        (self.root / ".hai_env/roles").mkdir()
        self.assertEqual(status(self.root)["status"], "partial")
        (self.root / ".hai_env/agents").rmdir()
        for state in ("prepared", "partial", "unexpected"):
            self.write_marker({"status": state})
            self.assertEqual(status(self.root)["status"], "partial")
            with self.assertRaises(SafetyError):
                require_ready(self.root)
        self.write_marker({"status": "completed"})
        self.assertEqual(status(self.root)["status"], "ready")
        (self.root / ".hai_env/config/agents").mkdir()
        self.assertEqual(status(self.root)["status"], "partial")

    def test_malformed_marker_blocks_without_changes(self):
        self.write_marker({"status": "completed"})
        path = self.root / MARKER
        path.write_text('{"status":"completed","status":"completed"}', encoding="utf-8")
        before = path.read_bytes()
        self.assertEqual(status(self.root)["status"], "partial")
        self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
