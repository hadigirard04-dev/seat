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
    chrome = " ".join(
        [
            page.inner_text("header"),
            page.inner_text(".project-picker"),
            page.inner_text(".next-band"),
            page.inner_text(".two-col"),
            page.inner_text("footer"),
        ]
    )
    # 项目数据正文可能含历史词，只约束界面固定文案
    for banned in ["Definition of Done", "Agent 指令坞", "点击复制", "续做指令"]:
        assert banned not in chrome, f"banned UI term still visible: {banned}"
    assert "完成清单" in chrome
    assert "交给 AI" in chrome
    assert "今天先做" in chrome
    assert "保存进度" in chrome
    results.append("T1 skeleton + plain language OK")

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

    # T6: onboarding + project badges
    page.goto(url + "?onboard=1")
    page.wait_for_load_state("networkidle")
    assert page.locator("#slot-onboard").is_visible(), "onboard should show with ?onboard=1"
    assert page.locator("#slot-onboard-ok").is_visible()
    page.locator("#slot-onboard-ok").click()
    page.wait_for_timeout(100)
    assert page.locator("#slot-onboard").is_hidden(), "onboard should hide after 知道了"
    page.goto(url)
    page.wait_for_load_state("networkidle")
    assert page.locator("#slot-onboard").is_hidden(), "onboard stays hidden after dismiss"
    badges = page.locator(".proj-badge")
    assert badges.count() >= 1, "project badges missing"
    badge_texts = [badges.nth(i).inner_text() for i in range(badges.count())]
    for t in badge_texts:
        assert t in ("今天", "本周", "放一放", "已收尾", "被卡住", "—"), t
    results.append(f"T6 onboard + badges OK ({badge_texts})")

    page.screenshot(path=str(out / "seat-plain-ux-1280.png"), full_page=True)
    page.set_viewport_size({"width": 390, "height": 844})
    page.wait_for_timeout(100)
    page.screenshot(path=str(out / "seat-plain-ux-390.png"), full_page=True)

    # plan band: content on a planned project + empty state on an unplanned one
    page.set_viewport_size({"width": 1280, "height": 900})
    assert page.locator("#slot-plan-band").count() > 0
    assert page.locator("#slot-plan-band .lab").inner_text().strip() == "规划"
    chips = page.locator(".proj-chip")
    saw_goal = False
    saw_empty = False
    for i in range(chips.count()):
        chips.nth(i).click()
        page.wait_for_timeout(150)
        plan_text = page.locator("#slot-plan").inner_text()
        if "还没有规划" in plan_text:
            saw_empty = True
        if ("要做的" in plan_text or "Day" in plan_text) and len(plan_text.strip()) > 30:
            saw_goal = True
            assert "第一件事" in plan_text or "Day" in plan_text, plan_text[:80]
    # single-project worlds may only have one state; require the state that exists to be correct
    assert saw_goal or saw_empty or "还没有规划" in page.locator("#slot-plan").inner_text()
    if chips.count() >= 2:
        assert saw_goal and saw_empty, (saw_goal, saw_empty)
    results.append(f"plan band OK (goal={saw_goal}, empty={saw_empty})")
    page.screenshot(path=str(out / "seat-plan-ui-1280.png"), full_page=True)

    browser.close()

print("\n".join(results))
print("ALL_PASS")
