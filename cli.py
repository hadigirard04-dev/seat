# -*- coding: utf-8 -*-
"""seat CLI — terminal view of the work desk (read-only + scan).

Usage:
  python cli.py                 # primary project summary
  python cli.py list            # all projects
  python cli.py show seat       # one project
  python cli.py prompt continue # print agent prompt
  python cli.py prompt verify|retro|handoff
  python cli.py scan            # refresh data/workspace.js
  python cli.py which           # paths

Exit codes: 0 ok, 1 usage/error, 2 not found.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT_CANDIDATES = 8


def lab_root() -> Path:
    probe = Path(__file__).resolve().parent
    for _ in range(ROOT_CANDIDATES):
        if (probe / "projects").is_dir() and ((probe / "AGENTS.md").exists() or (probe / "CURRENT.md").exists()):
            return probe
        probe = probe.parent
    return Path(__file__).resolve().parent


def data_path(root: Path) -> Path:
    return Path(__file__).resolve().parent / "data" / "workspace.json"


def load_data(root: Path) -> dict:
    path = data_path(root)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    # auto-scan once
    scan(root)
    return json.loads(path.read_text(encoding="utf-8"))


def scan(root: Path) -> None:
    script = Path(__file__).resolve().parent / "scripts" / "scan_workspace.py"
    subprocess.run(
        [sys.executable, str(script), "--root", str(root)],
        check=True,
    )


def find_project(data: dict, name: str | None) -> dict:
    projects = data.get("projects") or []
    if not projects:
        raise SystemExit("no projects found — run: python cli.py scan")
    if not name:
        pid = data.get("primaryId")
        for p in projects:
            if p.get("id") == pid:
                return p
        return projects[0]
    for p in projects:
        if p.get("name") == name or p.get("id") == name:
            return p
    raise SystemExit(f"project not found: {name}")


def prompt_text(kind: str, p: dict) -> str:
    name = p.get("name") or p.get("id")
    goal = p.get("goal") or ""
    stage = p.get("stage") or ""
    nxt = p.get("nextAction") or ""
    templates = {
        "continue": f"继续做项目「{name}」。只做这一件：{nxt}。做完更新 STATUS 与 docs/log，不要扩散范围，不要做未授权的 push。",
        "verify": f"请对「{name}」按 PLAN/DoD 逐项验收。每项给出可观察证据；缺证据标 failed，不要报喜。当前下一步是：{nxt}。",
        "retro": f"对「{name}」做简短复盘：完成项、卡点、可复用经验写入 docs/log.md 与 lessons（如有）。不要虚构未做的事。",
        "handoff": f"交接「{name}」：目标是 {goal} 阶段={stage}，下一步={nxt}。DoD 未完成项请列出。忽略无关工作区历史。",
    }
    if kind not in templates:
        raise SystemExit(f"unknown prompt: {kind} (use continue|verify|retro|handoff)")
    return templates[kind]


def print_project(p: dict, verbose: bool = True) -> None:
    print(f"name    : {p.get('name')}")
    print(f"path    : {p.get('path')}")
    print(f"stage   : {p.get('stage')}")
    print(f"updated : {p.get('updatedLabel')}")
    print(f"next    : {p.get('nextAction')}")
    dod = p.get("dod") or []
    done = sum(1 for d in dod if d.get("done"))
    print(f"dod     : {done}/{len(dod)}")
    if verbose and dod:
        for i, d in enumerate(dod, 1):
            mark = "x" if d.get("done") else " "
            print(f"  [{mark}] {i:02d} {d.get('label')}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="seat", description="开工屏 CLI（只读 + scan）")
    ap.add_argument("command", nargs="?", default="", help="list|show|prompt|scan|which|status")
    ap.add_argument("arg", nargs="?", default="", help="project name or prompt kind")
    args = ap.parse_args(argv)

    root = lab_root()
    cmd = (args.command or "status").lower()

    if cmd in ("which", "paths"):
        print(f"root    : {root}")
        print(f"data    : {data_path(root)}")
        print(f"scanner : {Path(__file__).resolve().parent / 'scripts' / 'scan_workspace.py'}")
        return 0

    if cmd == "scan":
        scan(root)
        data = load_data(root)
        print(f"scanned {len(data.get('projects') or [])} project(s); primary={data.get('primaryId')}")
        return 0

    data = load_data(root)

    if cmd in ("status", "st", "next", ""):
        if cmd == "next":
            p = find_project(data, args.arg or None)
            print(p.get("nextAction"))
            return 0
        p = find_project(data, args.arg or None)
        print_project(p, verbose=True)
        return 0

    if cmd in ("list", "ls"):
        for p in data.get("projects") or []:
            nxt = (p.get("nextAction") or "")[:50]
            print(f"- {p.get('name'):12}  {p.get('stage', ''):12}  {nxt}")
        if not data.get("projects"):
            print("(no projects)")
        return 0

    if cmd == "show":
        if not args.arg:
            raise SystemExit("usage: seat show <name>")
        p = find_project(data, args.arg)
        print_project(p, verbose=True)
        return 0

    if cmd == "prompt":
        kind = args.arg or "continue"
        p = find_project(data, None)
        print(prompt_text(kind, p))
        return 0

    raise SystemExit(f"unknown command: {cmd}\ntry: status|list|show|prompt|scan|which")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        print(f"seat error: {e}", file=sys.stderr)
        raise SystemExit(1)
