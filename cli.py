# -*- coding: utf-8 -*-
"""seat CLI — work desk in the terminal.

Read:
  python cli.py
  python cli.py list
  python cli.py show seat
  python cli.py next
  python cli.py prompt continue|verify|retro|handoff
  python cli.py which

Write:
  python cli.py next "新的下一步"
  python cli.py log "记一笔"
  python cli.py check "DoD 标签" [--off]
  python cli.py apply            # data/writeback.json
  python cli.py scan
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "scripts"))


def lab_root() -> Path:
    probe = HERE
    for _ in range(8):
        if (probe / "projects").is_dir() and ((probe / "AGENTS.md").exists() or (probe / "CURRENT.md").exists()):
            return probe
        probe = probe.parent
    return HERE


def project_dir(data: dict, name: str | None) -> Path:
    p = find_project(data, name)
    path = Path(p.get("path") or "")
    if path.is_dir():
        return path
    # status under worktree: use parent project folder if path is worktree
    if path.name == "seat-demo" and path.parent.name == ".worktrees":
        return path.parents[1]
    return path


def data_path() -> Path:
    return HERE / "data" / "workspace.json"


def load_data(root: Path) -> dict:
    path = data_path()
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    scan(root)
    return json.loads(path.read_text(encoding="utf-8"))


def scan(root: Path) -> None:
    subprocess.run([sys.executable, str(HERE / "scripts" / "scan_workspace.py"), "--root", str(root)], check=True)


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
    git = p.get("git") or {}
    if git.get("available"):
        print(f"git     : {git.get('branch')} · {len(git.get('commits') or [])} commit(s)")
    tl = p.get("timeline") or []
    print(f"timeline: {len(tl)} entr(ies)")
    if verbose and dod:
        for i, d in enumerate(dod, 1):
            mark = "x" if d.get("done") else " "
            print(f"  [{mark}] {i:02d} {d.get('label')}")


def run_write(kind: str, args: argparse.Namespace, data: dict) -> int:
    from writeback import apply_writeback_payload, append_log, find_status, set_checkbox, set_next_action

    name = None
    root = lab_root()
    pdir = Path(find_project(data, name).get("path") or root / "projects" / "seat")
    if not pdir.exists():
        pdir = root / "projects" / "seat"

    from writeback import find_status

    status = find_status(pdir)
    if status is not None:
        write_root = status.parent
    else:
        write_root = pdir

    if kind == "set-next":
        status = find_status(write_root)
        if not status:
            raise SystemExit(f"STATUS.md not found under {write_root}")
        text = set_next_action(status, args.arg)
        print(f"updated next in {status}")
        print(text)
        scan(root)
        return 0

    if kind == "log":
        path = append_log(write_root, args.arg)
        print(f"appended {path}")
        return 0

    if kind == "check":
        label = args.arg
        done = not args.off
        files = set_checkbox(write_root, label, done)
        if not files:
            files = set_checkbox(pdir, label, done)
        if not files:
            raise SystemExit(f"no checkbox matched: {label}")
        for f in files:
            print(f"updated {f}")
        scan(root)
        return 0

    if kind == "apply":
        payload_path = HERE / "data" / "writeback.json"
        if not payload_path.exists():
            raise SystemExit("data/writeback.json not found — export from the web UI first")
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
        report = apply_writeback_payload(write_root, payload)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        scan(root)
        return 0

    raise SystemExit(f"unknown write command: {kind}")


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
        sys.stderr.reconfigure(line_buffering=True)
    except Exception:
        pass
    ap = argparse.ArgumentParser(prog="seat", description="开工屏 CLI")
    ap.add_argument("command", nargs="?", default="status")
    ap.add_argument("arg", nargs="?", default="")
    ap.add_argument("--off", action="store_true", help="check: mark unchecked")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    root = lab_root()
    cmd = args.command.lower()

    if cmd == "which":
        print(f"root    : {root}")
        print(f"data    : {data_path()}")
        print(f"scanner : {HERE / 'scripts' / 'scan_workspace.py'}")
        print(f"write   : {HERE / 'scripts' / 'writeback.py'}")
        return 0

    if cmd == "scan":
        scan(root)
        data = load_data(root)
        print(f"scanned {len(data.get('projects') or [])} project(s); primary={data.get('primaryId')}")
        return 0

    if cmd in ("next", "set-next", "log", "check", "apply"):
        data = load_data(root)
        # bare `seat next` → print; `seat next "text"` → write
        if cmd == "next" and not args.arg:
            p = find_project(data, None)
            print(p.get("nextAction"))
            return 0
        if cmd == "next" and args.arg:
            return run_write("set-next", args, data)
        return run_write(cmd if cmd != "set-next" else "set-next", args, data)

    data = load_data(root)

    if cmd in ("status", "st", ""):
        p = find_project(data, args.arg or None)
        print_project(p, verbose=True)
        return 0

    if cmd in ("list", "ls"):
        for p in data.get("projects") or []:
            nxt = (p.get("nextAction") or "")[:50]
            print(f"- {p.get('name'):12}  {p.get('stage', '')[:18]:18}  {nxt}")
        return 0

    if cmd == "show":
        if not args.arg:
            raise SystemExit("usage: seat show <name>")
        print_project(find_project(data, args.arg), verbose=True)
        return 0

    if cmd == "prompt":
        print(prompt_text(args.arg or "continue", find_project(data, None)))
        return 0

    raise SystemExit(f"unknown command: {cmd}\ntry: status|list|show|prompt|next|log|check|apply|scan|which")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        print(f"seat error: {e}", file=sys.stderr)
        raise SystemExit(1)
