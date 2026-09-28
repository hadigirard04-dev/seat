# -*- coding: utf-8 -*-
"""Scan the GitHub lab workspace into data/workspace.js for seat.

Usage:
  python scripts/scan_workspace.py
  python scripts/scan_workspace.py --root "C:/path/to/GitHub 小玩意"

Reads CURRENT.md and projects/*/STATUS.md (+ worktrees). Writes UTF-8
data/workspace.js so the page works from file:// via <script src>.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_bullets(text: str) -> list[str]:
    items = []
    for line in text.splitlines():
        m = re.match(r"^\s*[-*+]\s+(?:\[[ xX]\]\s+)?(.+)$", line)
        if m:
            items.append(m.group(1).strip())
    return items


def parse_dod(text: str) -> list[dict]:
    dod = []
    for line in text.splitlines():
        m = re.match(r"^\s*[-*+]\s+\[([ xX])\]\s+(.+)$", line)
        if m:
            done = m.group(1).lower() == "x"
            dod.append({"id": f"d{len(dod)+1}", "label": m.group(2).strip(), "done": done})
        else:
            m2 = re.match(r"^\s*[-*+]\s+(?:core_functionality|tests|readme)\b", line)
            _ = m2
    # also accept "- [x] label" style from PLAN
    return dod


def parse_status(path: Path) -> dict:
    text = read_text(path)
    name = path.parent.name
    title = re.search(r"^#\s+STATUS\s*[·\-–—]?\s*(.+)$", text, re.M)
    if title and title.group(1).strip():
        name = title.group(1).strip()

    stage = ""
    next_action = ""
    updated = ""
    for line in text.splitlines():
        if "阶段" in line and "：" in line:
            stage = line.split("：", 1)[1].strip()
        if line.strip().startswith("- 更新") or "最后更新" in line:
            updated = line.split("：", 1)[-1].strip()
        if "下一步" in line and next_action == "":
            # inline next on same bullet
            part = line.split("：", 1)
            if len(part) == 2 and part[1].strip():
                next_action = part[1].strip()

    # section 下一步
    if not next_action:
        m = re.search(r"##\s*下一步\s*\n+([\s\S]+?)(?:\n##\s|\Z)", text)
        if m:
            lines = [ln.strip() for ln in m.group(1).strip().splitlines() if ln.strip()]
            if lines:
                next_action = re.sub(r"^[-*+]\s+", "", lines[0])

    if not next_action:
        m = re.search(r"##\s*下一步（未做[^\n]*\n+([\s\S]+?)(?:\n##\s|\Z)", text)
        if m:
            lines = [ln.strip() for ln in m.group(1).strip().splitlines() if ln.strip()]
            if lines:
                next_action = re.sub(r"^[-*+]\s+", "", lines[0])

    # STATUS file may put next on a bullet under 下一步
    if not next_action:
        in_next = False
        for line in text.splitlines():
            if re.match(r"^##\s*下一步", line):
                in_next = True
                continue
            if in_next and line.startswith("## "):
                break
            if in_next and line.strip():
                next_action = re.sub(r"^[-*+]\s+", "", line.strip())
                break

    dod = parse_dod(text)
    plan = path.parent / "PLAN.md"
    if not dod and plan.exists():
        dod = parse_dod(read_text(plan))
    if not dod:
        spec_dir = path.parent / "docs" / "compose" / "spec"
        if spec_dir.is_dir():
            for spec in sorted(spec_dir.glob("*.md")):
                dod = parse_dod(read_text(spec))
                if dod:
                    break

    goal = ""
    gm = re.search(r"^- 阶段：(.+)$", text, re.M)
    if gm:
        goal = gm.group(1).strip()

    return {
        "name": name,
        "path": str(path.parent).replace("\\", "/"),
        "statusFile": str(path).replace("\\", "/"),
        "stage": stage or "进行中",
        "goal": goal or stage or "",
        "nextAction": next_action or "（STATUS 未写「下一步」）",
        "updatedLabel": updated or "未知",
        "dod": dod,
        "risk": "",
    }


def parse_current(root: Path) -> dict:
    path = root / "CURRENT.md"
    if not path.exists():
        return {}
    text = read_text(path)
    current = {}
    m = re.search(r"##\s*当前项目\s*\n+([\s\S]+?)(?:\n##\s|\Z)", text)
    if m:
        block = m.group(1).strip().splitlines()
        if block:
            current["title"] = block[0].strip().strip("*")
    m2 = re.search(r"##\s*下一步\s*\n+([\s\S]+?)(?:\n##\s|\Z)", text)
    if m2:
        lines = [ln.strip() for ln in m2.group(1).strip().splitlines() if ln.strip()]
        if lines:
            current["nextAction"] = re.sub(r"^[-*+]\s+", "", lines[0])
    return current


def scan(root: Path) -> dict:
    projects = []
    seen = set()
    pdir = root / "projects"
    if pdir.exists():
        for status in sorted(pdir.rglob("STATUS.md")):
            # prefer worktree status when present; key by project folder name under projects/
            rel = status.relative_to(pdir)
            key = rel.parts[0] if rel.parts else status.stem
            info = parse_status(status)
            info["id"] = key
            if key in seen:
                # replace with richer worktree status
                projects = [p for p in projects if p["id"] != key]
            seen.add(key)
            projects.append(info)

    current = parse_current(root)
    primary = None
    if projects:
        # prefer project named in CURRENT or the one with latest status path containing seat
        title = current.get("title", "")
        for p in projects:
            if p["name"] in title or p["id"] in title:
                primary = p["id"]
        if not primary:
            primary = projects[0]["id"]

    return {
        "generatedAt": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "current": current,
        "projects": projects,
        "primaryId": primary,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="", help="lab workspace root (folder containing projects/)")
    ap.add_argument("--out", default="", help="output dir for workspace.js/json")
    args = ap.parse_args()

    script = Path(__file__).resolve()
    default_root = script.parents[2]  # .../GitHub 小玩意/scripts/scan -> seat? careful
    # scripts/ is under seat-demo worktree; lab root is two levels above projects/seat
    # Prefer: walk up until we find projects/ or CURRENT.md
    root = Path(args.root) if args.root else None
    if root is None:
        probe = script.parent
        for _ in range(8):
            if (probe / "projects").is_dir() or (probe / "CURRENT.md").exists():
                if (probe / "projects").is_dir() or (probe / "AGENTS.md").exists():
                    root = probe
                    break
            probe = probe.parent
        if root is None:
            root = default_root

    root = root.resolve()
    data = scan(root)
    out_dir = Path(args.out) if args.out else (script.parents[1] / "data")
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = json.dumps(data, ensure_ascii=False, indent=2)
    (out_dir / "workspace.json").write_text(payload, encoding="utf-8")
    (out_dir / "workspace.js").write_text(
        "window.SEAT_DATA = " + payload + ";\n",
        encoding="utf-8",
    )
    print(f"root={root}")
    print(f"projects={len(data['projects'])} primary={data['primaryId']}")
    for p in data["projects"]:
        print(f"  - {p['name']}: {p['nextAction'][:60]}")
    print(f"wrote {out_dir / 'workspace.js'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
