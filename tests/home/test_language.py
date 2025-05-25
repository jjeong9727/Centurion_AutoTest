import pytest
import json
from pathlib import Path
from playwright.sync_api import Page, expect
from config import URLS

# 언어 매핑 로딩 함수
def load_language_mapping(path: Path = Path("data/language.json")):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# 화면에 노출되는지 확인하는 함수
def verify_translations_visible(page: Page, lang: str, mapping: dict):
    for key, val in mapping.items():
        expected_text = val.get(lang)
        if not expected_text:
            continue

        # 예약어 " 포함 시 정확 매칭 방지 위해 has_text 사용
        locator = page.locator(f"text={expected_text}")
        try:
            locator.scroll_into_view_if_needed(timeout=2000)
            expect(locator).to_be_visible(timeout=3000)
            print(f"✅ '{expected_text}' is visible.")
        except:
            print(f"❌ '{expected_text}' is NOT visible.")
            raise  # 실패 시 테스트 실패 처리

# 메인 테스트
def test_language_display_after_switch(page: Page):
    mapping = load_language_mapping()
    page.goto(URLS["home_main"])

    # --- Korean 확인 ---
    page.locator("button:has-text('KOR')").click()
    page.locator("a:has-text('Korean')").click()
    verify_translations_visible(page, "ko", mapping)

    # --- English 확인 ---
    page.locator("button:has-text('KOR')").click()
    page.locator("a:has-text('English')").click()
    verify_translations_visible(page, "en", mapping)
