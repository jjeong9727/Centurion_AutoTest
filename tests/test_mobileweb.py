import json
from playwright.sync_api import sync_playwright
from config import URLS

with open("data/device_profiles.json", "r", encoding="utf-8") as f:
    device_profiles = json.load(f)

def is_ios_device(profile: dict) -> bool:
    ua = profile.get("user_agent", "")
    return "iPhone" in ua or "iOS" in ua

def test_run_mobile_test(device_name: str):
    profile = device_profiles[device_name]

    with sync_playwright() as p:
        # 브라우저 선택: iPhone이면 WebKit(Safari), 아니면 Chromium(Chrome)
        browser = (
            p.webkit.launch(headless=False)
            if is_ios_device(profile)
            else p.chromium.launch(headless=False)
        )

        context = browser.new_context(**profile)
        page = context.new_page()
        page.goto(URLS["home_main"])
        page.screenshot(path=f"screenshots/{device_name}.png")
        browser.close()

# 실행
for device_name in device_profiles:
    test_run_mobile_test(device_name)
