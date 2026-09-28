# -*- coding: utf-8 -*-
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
designs = root / "designs"
out = root / "docs" / "compose" / "shots"
out.mkdir(parents=True, exist_ok=True)

pages = ["v1-ink.html", "v2-console.html", "v3-bloom.html"]

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge")
    context = browser.new_context(
        viewport={"width": 1280, "height": 900},
        permissions=["clipboard-read", "clipboard-write"],
    )
    page = context.new_page()
    for name in pages:
        url = (designs / name).as_uri()
        page.goto(url)
        page.wait_for_timeout(200)
        # next action filled
        next_text = page.locator("#slot-next").inner_text()
        assert next_text and next_text != "—", (name, next_text)
        # dod list
        items = page.locator("#slot-dod .dod-item").count()
        assert items >= 5, (name, items)
        # toggle first checkbox
        cb = page.locator("#slot-dod input:not(:checked)").first
        if cb.count() == 0:
            cb = page.locator("#slot-dod input").first
        before = page.locator("#slot-count").inner_text()
        cb.check()
        after = page.locator("#slot-count").inner_text()
        assert before != after, (name, before, after)
        # copy continue
        page.locator("#slot-copy-continue").click()
        page.wait_for_timeout(150)
        clip = page.evaluate("() => navigator.clipboard.readText()")
        assert "seat" in clip or "下一步" in clip or "继续做" in clip, (name, clip[:80])
        page.screenshot(path=str(out / f"design-{name.replace('.html','')}.png"), full_page=True)
        print(name, "OK", "->", after)
    # narrow shot for v3
    page.goto((designs / "v3-bloom.html").as_uri())
    page.set_viewport_size({"width": 390, "height": 844})
    page.wait_for_timeout(150)
    overflow = page.evaluate(
        "() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1"
    )
    assert not overflow
    page.screenshot(path=str(out / "design-v3-bloom-390.png"), full_page=True)
    print("390 OK")
    browser.close()
print("ALL_PASS")
