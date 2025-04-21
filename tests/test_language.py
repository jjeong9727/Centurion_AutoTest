import pytest
import json
from playwright.sync_api import Page

LANGUAGE_CODES = ["ko", "en", "ja", "zh-cn", "th", "vi"]

# JSON 불러오기 함수
def load_language_mapping(path="json/language.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# 메뉴 진입 및 텍스트 확인 함수
def navigate_and_check_texts(page: Page, texts: dict, lang_code: str):
    page.wait_for_timeout(1000)

    # 1. DAYBEAU hover
    page.hover("text=DAYBEAU CLINIC")
    page.wait_for_timeout(500)

    # 2. '컨투어링' 메뉴 hover → menu_Txt 클릭
    section = page.locator(".menu_title", has_text=texts["subtitle1"][lang_code])
    section.hover()
    page.wait_for_timeout(500)
    section.locator("xpath=following-sibling::div//div[contains(@class, 'menu_Txt')]").first.click()

    # 3. 컨투어링 페이지 도착 확인
    page.wait_for_selector(".sub_title1")
    assert texts["subtitle1"][lang_code] in page.inner_text(".sub_title1")

    # 4. 첫 번째 시술 항목 클릭
    page.locator(".procedure_info li").first.click()
    page.wait_for_selector(".subtitle1")

    # 5. 최종 페이지 텍스트 확인
    assert texts["subtitle1"][lang_code] in page.inner_text(".subtitle1")
    assert texts["rline_on"][lang_code] in page.inner_text(".rline.on")
    assert texts["title"][lang_code] in page.inner_text(".title")

# 기본 한국어 확인
@pytest.mark.order(1)
def test_korean_default(page: Page):
    texts = load_language_mapping()
    page.goto("https://daybeauclinic01.com/branch/")
    navigate_and_check_texts(page, texts, "ko")

# 다른 언어 확인 (영어~베트남어)
@pytest.mark.order(2)
@pytest.mark.parametrize("lang_idx,lang_code", list(enumerate(LANGUAGE_CODES[1:])))  # ko 제외
def test_other_languages(page: Page, lang_idx, lang_code):
    texts = load_language_mapping()
    page.goto("https://daybeauclinic01.com/branch/")

    # 언어 선택 열기
    page.click(".language2")
    page.locator(".list.translation-links li").nth(lang_idx + 1).click()  # +1은 ko 제외 보정
    page.wait_for_timeout(1000)

    navigate_and_check_texts(page, texts, lang_code)
