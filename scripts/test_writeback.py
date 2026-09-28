# -*- coding: utf-8 -*-
"""Unit tests for writeback helpers."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import writeback as wb  # noqa: E402


class WritebackTests(unittest.TestCase):
    def test_append_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            path = wb.append_log(p, "hello")
            text = path.read_text(encoding="utf-8")
            self.assertIn("hello", text)
            self.assertIn("# docs/log", text)

    def test_set_next_action_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            status = Path(tmp) / "STATUS.md"
            status.write_text("# STATUS · t\n\n## 下一步\n\n旧的\n", encoding="utf-8")
            wb.set_next_action(status, "新的下一步")
            text = status.read_text(encoding="utf-8")
            self.assertIn("新的下一步", text)
            self.assertNotIn("旧的", text)

    def test_set_checkbox(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "PLAN.md").write_text("- [ ] T1 do thing\n", encoding="utf-8")
            files = wb.set_checkbox(p, "T1 do thing", True)
            self.assertTrue(files)
            text = (p / "PLAN.md").read_text(encoding="utf-8")
            self.assertIn("[x]", text)


if __name__ == "__main__":
    unittest.main()
