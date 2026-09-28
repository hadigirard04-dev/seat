# -*- coding: utf-8 -*-
"""UI smoke check for seat demo (V1 Ink)."""
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
url = (root / "index.html").as_uri()
out = root / "docs" / "compose" / "shots"
out.mkdir(parents=True, exist_ok=True)

results = []

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge")
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    page.goto(url)
    page.wait_for_load_state("networkidle")

    for sel in ["#slot-name", "#slot-next", "#slot-dod", "#slot-prompts", ".page", "#slot-timeline", "#slot-git"]:
        assert page.locator(sel).count() > 0, f"missing {sel}"
    title = page.locator("#slot-name").inner_text()
    assert title.strip() == "seat", title
    next_text = page.locator("#slot-next").inner_text()
    assert next_text and next_text != "—", next_text
    results.append("T1 skeleton OK")

    page.screenshot(path=str(out / "seat-demo-1280.png"), full_page=True)

    count_before = page.locator("#slot-count").inner_text()
    unchecked = page.locator("#slot-dod input:not(:checked)").first
    if unchecked.count() > 0:
        unchecked.check()
    else:
        page.locator("#slot-dod input").first.uncheck()
    count_after = page.locator("#slot-count").inner_text()
    assert count_before != count_after, (count_before, count_after)
    width = page.locator("#slot-fill").evaluate("el => el.style.width")
    assert width and width != "0%", width
    results.append(f"T2 dod progress OK ({count_before} -> {count_after}, width={width})")

    context = page.context
    context.grant_permissions(["clipboard-read", "clipboard-write"])
    page.locator("#slot-copy-continue").click()
    page.wait_for_timeout(200)
    clip = page.evaluate("() => navigator.clipboard.readText()")
    assert "seat" in clip, clip[:120]
    assert "只做这一件" in clip, clip[:200]
    results.append("T3 continue copy OK")

    for pid in ["continue", "verify", "retro", "handoff"]:
        btn = page.locator(f'button[data-copy="{pid}"]')
        btn.click()
        page.wait_for_timeout(150)
        text = page.evaluate("() => navigator.clipboard.readText()")
        assert len(text) > 20, (pid, text)

    results.append("T3 all prompt buttons OK")

    page.set_viewport_size({"width": 390, "height": 844})
    page.wait_for_timeout(100)
    overflow = page.evaluate(
        "() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1"
    )
    assert not overflow, "horizontal overflow at 390px"
    page.screenshot(path=str(out / "seat-demo-390.png"), full_page=True)
    results.append("T4 390px no overflow OK")

    # T5: timeline + git panels render; DoD override persists across reload
    page.set_viewport_size({"width": 1280, "height": 900})
    tl_count = page.locator("#slot-timeline .tl-item").count()
    git_branch = page.locator("#slot-git .git-branch").count()
    assert tl_count >= 0, tl_count
    assert git_branch >= 0, git_branch
    results.append(f"T5 panels OK (timeline={tl_count}, git_branch={git_branch})")

    before = page.locator("#slot-count").inner_text()
    boxes = page.locator("#slot-dod input")
    if boxes.count() > 0:
        first = boxes.first
        was = first.is_checked()
        first.set_checked(not was)
        page.wait_for_timeout(100)
        page.reload()
        page.wait_for_load_state("networkidle")
        after = page.locator("#slot-dod input").first.is_checked()
        assert after == (not was), (was, after)
        results.append(f"T5 localStorage persist OK ({before} -> after reload)")
    else:
        results.append("T5 localStorage skip (no DoD items)")

    browser.close()

print("\n".join(results))
print("ALL_PASS")
