import pytest
import json
from pathlib import Path
from playwright.sync_api import Page, expect
from config import URLS, is_mobile

def load_language_mapping(path: Path = Path("data/language.json")):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def scroll_to_find_element(page: Page, text: str, exact=True, timeout=3000, max_scroll=6000, step=300, wait_per_step=1000):
    """텍스트가 화면에 등장할 때까지 조금씩 스크롤하며 탐색"""
    print(f"🔍 '{text}' 텍스트 탐색 시작...")
    scrolled = 0

    while scrolled <= max_scroll:
        locator = page.get_by_text(text, exact=exact)

        if locator.count() > 0:
            try:
                locator.first.scroll_into_view_if_needed(timeout=timeout)
                expect(locator.first).to_be_visible(timeout=timeout)
                print(f"✅ '{text}' 텍스트 확인 완료 (스크롤 {scrolled}px)")
                return locator.first
            except Exception as e:
                print(f"⚠️ '{text}' 텍스트가 시야에 아직 보이지 않음. 다시 스크롤합니다.")
        else:
            print(f"ℹ️ '{text}' 텍스트가 아직 DOM에 없음. {wait_per_step}ms 대기 후 재시도")

        page.evaluate(f"() => window.scrollBy(0, {step})")
        page.wait_for_timeout(wait_per_step)
        scrolled += step

    raise AssertionError(f"❌ '{text}' 텍스트가 최대 {max_scroll}px 스크롤 후에도 보이지 않음")

def verify_translations_visible(page: Page, lang: str, mapping: dict):
    for key, val in mapping.items():
        expected_text = val.get(lang)
        if not expected_text:
            continue

        try:
            if is_mobile:
                locator = scroll_to_find_element(page, expected_text, exact=False, wait_per_step=2000)
            else:
                locator = page.locator(f"*:has-text('{expected_text}')").first
                locator.scroll_into_view_if_needed(timeout=3000)
                expect(locator).to_be_visible(timeout=3000)

            print(f"✅ '{expected_text}' 포함 여부 확인 완료")
        except Exception:
            print(f"❌ '{expected_text}' 포함 여부 확인 실패")
            raise

def test_language_display_after_switch(page: Page):
    mapping = load_language_mapping()

    page.goto(URLS["home_main"])
    page.wait_for_timeout(2000)

    # --- 한국어 확인 ---
    page.locator("button:has-text('KOR')").click()
    page.wait_for_timeout(500)
    page.locator("a:has-text('Korean')").click()
    page.wait_for_timeout(2000)
    verify_translations_visible(page, "ko", mapping)

    # --- 영어 확인 ---
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)
    page.locator("button:has-text('KOR')").click()
    page.wait_for_timeout(500)
    page.locator("a:has-text('English')").click()
    page.wait_for_timeout(2000)
    verify_translations_visible(page, "en", mapping)
