# -*- coding: utf-8 -*-
"""Unit tests for scan_workspace helpers (no network, no Playwright)."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import scan_workspace as sw  # noqa: E402


class ParseDodTests(unittest.TestCase):
    def test_checked_and_unchecked(self):
        text = "- [x] done item\n- [ ] todo item\n- plain bullet\n"
        dod = sw.parse_dod(text)
        self.assertEqual(len(dod), 2)
        self.assertTrue(dod[0]["done"])
        self.assertFalse(dod[1]["done"])
        self.assertEqual(dod[0]["label"], "done item")


class ParseTimelineTests(unittest.TestCase):
    def test_sections_and_bullets(self):
        with tempfile.TemporaryDirectory() as tmp:
            pdir = Path(tmp)
            docs = pdir / "docs"
            docs.mkdir()
            (docs / "log.md").write_text(
                "# docs/log\n\n"
                "## 2026-09-28\n"
                "- first entry\n"
                "## 2026-09-29 · UI\n"
                "- second entry\n"
                "- 2026-09-30 · dated bullet\n",
                encoding="utf-8",
            )
            items = sw.parse_timeline(pdir)
            self.assertGreaterEqual(len(items), 3)
            self.assertEqual(items[0]["date"], "2026-09-30")
            self.assertIn("dated bullet", items[0]["text"])
            dates = [i["date"] for i in items]
            self.assertEqual(dates, sorted(dates, reverse=True))

    def test_missing_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(sw.parse_timeline(Path(tmp)), [])


class GitInfoTests(unittest.TestCase):
    def test_non_git_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            info = sw.git_info(Path(tmp))
            self.assertFalse(info["available"])
            self.assertEqual(info["commits"], [])


class ScanSmokeTests(unittest.TestCase):
    def test_scan_includes_timeline_git_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            proj = root / "projects" / "demo"
            proj.mkdir(parents=True)
            (proj / "STATUS.md").write_text(
                "# STATUS · demo\n\n- 阶段：进行中\n\n## 下一步\n\n写一个测试\n",
                encoding="utf-8",
            )
            (proj / "docs").mkdir()
            (proj / "docs" / "log.md").write_text(
                "# docs/log\n\n## 2026-09-28\n- boot\n", encoding="utf-8"
            )
            data = sw.scan(root)
            self.assertEqual(len(data["projects"]), 1)
            p = data["projects"][0]
            self.assertIn("timeline", p)
            self.assertIn("git", p)
            self.assertEqual(p["nextAction"], "写一个测试")
            self.assertEqual(p["timeline"][0]["text"], "boot")


class PayloadShapeTests(unittest.TestCase):
    def test_json_roundtrip(self):
        sample = {
            "generatedAt": "2026-09-28T00:00:00",
            "root": "~/lab",
            "projects": [
                {
                    "id": "x",
                    "name": "x",
                    "timeline": [{"date": "2026-09-28", "text": "t", "kind": "item"}],
                    "git": {"available": False, "branch": "", "commits": []},
                }
            ],
            "primaryId": "x",
        }
        raw = json.dumps(sample, ensure_ascii=False)
        back = json.loads(raw)
        self.assertEqual(back["projects"][0]["timeline"][0]["date"], "2026-09-28")


if __name__ == "__main__":
    unittest.main()
