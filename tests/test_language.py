import pytest
import json
from pathlib import Path
from playwright.sync_api import Page, expect
from config import URLS

# 언어 매핑 로딩 함수
def load_language_mapping(path: Path = Path("data/language.json")):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def verify_translations_visible(page: Page, lang: str, mapping: dict):
    for key, val in mapping.items():
        expected_text = val.get(lang)
        if not expected_text:
            continue

        # 정확히 일치하는 모든 요소 가져오기
        locators = page.get_by_text(expected_text, exact=True)

        try:
            count = locators.count()
            if count == 0:
                raise AssertionError(f"❌ '{expected_text}' is NOT found on page.")

            for i in range(count):
                locator = locators.nth(i)
                locator.scroll_into_view_if_needed(timeout=2000)
                expect(locator).to_be_visible(timeout=3000)

            print(f"✅ '{expected_text}' is visible ({count}개 발견됨).")
        except Exception as e:
            print(f"❌ '{expected_text}' is NOT fully visible.")
            raise


# 메인 테스트
def test_language_display_after_switch(page: Page):
    mapping = load_language_mapping()
    page.goto(URLS["home_main"])
    page.wait_for_timeout(2000)

    # --- Korean 확인 ---
    page.locator("button:has-text('KOR')").click()
    page.wait_for_timeout(1000)
    page.locator("a:has-text('Korean')").click()
    page.wait_for_timeout(3000)
    verify_translations_visible(page, "ko", mapping)

    # --- English 확인 ---
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(2000)
    page.locator("button:has-text('KOR')").click()
    page.wait_for_timeout(1000)
    page.locator("a:has-text('English')").click()
    page.wait_for_timeout(3000)
    verify_translations_visible(page, "en", mapping)
