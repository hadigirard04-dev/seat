# -*- coding: utf-8 -*-
"""Write-back helpers for seat: STATUS.md and docs/log.md."""
from __future__ import annotations

import re
from pathlib import Path


def _ensure_docs_log(project_dir: Path) -> Path:
    docs = project_dir / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    path = docs / "log.md"
    if not path.exists():
        path.write_text("# docs/log\n\n", encoding="utf-8")
    return path


def append_log(project_dir: Path, entry: str, date: str | None = None) -> Path:
    path = _ensure_docs_log(project_dir)
    text = path.read_text(encoding="utf-8")
    stamp = date or __import__("datetime").date.today().isoformat()
    line = f"- {stamp} · {entry.strip()}"
    if not text.endswith("\n"):
        text += "\n"
    if text.rstrip() == "# docs/log":
        text = f"# docs/log\n\n{line}\n"
    else:
        text = text.rstrip() + "\n" + line + "\n"
    path.write_text(text, encoding="utf-8")
    return path


def find_status(project_dir: Path) -> Path | None:
    direct = project_dir / "STATUS.md"
    if direct.exists():
        return direct
    # worktree status preferred when working from repo root
    wts = sorted(project_dir.glob(".worktrees/*/STATUS.md"))
    if wts:
        return wts[-1]
    return None


def set_next_action(status_path: Path, next_action: str) -> str:
    text = status_path.read_text(encoding="utf-8")
    body = next_action.strip()
    if not body:
        raise ValueError("next action is empty")

    # Replace inline "下一步..." bullet
    pattern_inline = re.compile(
        r"(^-\s*下一步[^：:]*[：:]\s*)(.+)$",
        re.M,
    )
    if pattern_inline.search(text):
        text = pattern_inline.sub(lambda m: m.group(1) + body, text, count=1)
    elif re.search(r"^##\s*下一步", text, re.M):
        # replace first non-empty line under ## 下一步
        def repl(m: re.Match[str]) -> str:
            return m.group(1) + body + "\n"

        text = re.sub(
            r"(##\s*下一步[^\n]*\n\n?)(?!\n)(.+)",
            repl,
            text,
            count=1,
        )
    else:
        text = text.rstrip() + f"\n\n## 下一步\n\n{body}\n"
    status_path.write_text(text, encoding="utf-8")
    return body


def set_stage(status_path: Path, stage: str) -> None:
    text = status_path.read_text(encoding="utf-8")
    if re.search(r"^-\s*阶段[：:]", text, re.M):
        text = re.sub(r"(^-\s*阶段[：:]\s*)(.+)$", lambda m: m.group(1) + stage.strip(), text, count=1, flags=re.M)
    else:
        text = text.replace("# STATUS", f"# STATUS\n\n- 阶段：{stage.strip()}", 1)
    status_path.write_text(text, encoding="utf-8")


def _toggle_checkbox_line(line: str, done: bool) -> str:
    m = re.match(r"^(\s*[-*+]\s+\[)([ xX])(\]\s+)(.*)$", line)
    if not m:
        return line
    mark = "x" if done else " "
    return f"{m.group(1)}{mark}{m.group(3)}{m.group(4)}"


def set_checkbox(project_dir: Path, label_query: str, done: bool, explicit_file: Path | None = None) -> list[Path]:
    """Toggle [ ]/[x] lines matching label_query. Returns files changed."""
    candidates: list[Path] = []
    if explicit_file:
        candidates.append(explicit_file)
    else:
        status = find_status(project_dir)
        if status:
            candidates.append(status)
        plan = project_dir / "PLAN.md"
        if plan.exists():
            candidates.append(plan)
        for p in project_dir.glob("docs/compose/spec/*.md"):
            candidates.append(p)
        for p in project_dir.glob(".worktrees/*/PLAN.md"):
            candidates.append(p)
        for p in project_dir.glob(".worktrees/*/docs/compose/spec/*.md"):
            candidates.append(p)
        for p in project_dir.glob(".worktrees/*/STATUS.md"):
            candidates.append(p)

    seen = set()
    touched: list[Path] = []
    q = label_query.strip().lower()
    for path in candidates:
        rp = path.resolve()
        if rp in seen or not path.exists():
            continue
        seen.add(rp)
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines(keepends=True)
        hit = False
        dirty = False
        for i, line in enumerate(lines):
            if re.match(r"^\s*[-*+]\s+\[[ xX]\]\s+", line) and q in line.lower():
                hit = True
                new_line = _toggle_checkbox_line(line.rstrip("\n"), done)
                nl = "\n" if line.endswith("\n") else ""
                if new_line + nl != line:
                    lines[i] = new_line + nl
                    dirty = True
        if dirty:
            path.write_text("".join(lines), encoding="utf-8")
        if hit:
            touched.append(path)
    return touched


def apply_writeback_payload(project_dir: Path, payload: dict) -> dict:
    """payload: {next?, stage?, log?, checks?: [{label, done}], project_dir?}"""
    report: dict = {"next": None, "stage": False, "log": None, "checks": [], "status_file": None}
    status = find_status(project_dir)
    report["status_file"] = str(status) if status else None

    if payload.get("stage") and status:
        set_stage(status, str(payload["stage"]))
        report["stage"] = True

    if payload.get("next") and status:
        report["next"] = set_next_action(status, str(payload["next"]))

    if payload.get("log"):
        report["log"] = str(append_log(project_dir, str(payload["log"])))

    for item in payload.get("checks") or []:
        label = str(item.get("label") or "")
        done = bool(item.get("done", True))
        files = set_checkbox(project_dir, label, done)
        report["checks"].append({"label": label, "done": done, "files": [str(f) for f in files]})

    return report
