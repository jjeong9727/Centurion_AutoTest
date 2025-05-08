import pytest
import json
from playwright.sync_api import Page
from config import URLS

LANGUAGE_CODES = ["ko", "en"]
LANGUAGE_TESTID = {
    "ko": "language_kor",
    "en": "language_eng"
}
PAGES_TO_TEST = [
    {"url": URLS["home_landing"], "keys": ["btn_removal", "btn_lifting"]},
    {"url": URLS["home_login"], "keys": ["txt_login", "btn_login", "header_reservation", "footer_branch"]},
    {"url": URLS["home_discover"], "keys": ["txt_lifting", "txt_removal", "btn_reservation"]},
    # {"url": URLS["home_previlege"], "keys": ["", ""]},
    {"url": URLS["home_removal"], "keys": ["txt_removal", "btn_reservation"]},
    {"url": URLS["home_lifting"], "keys": ["txt_lifting"]},
    {"url": URLS["home_mypage_profile"], "keys": ["txt_mypage", "txt_profile"]},
    {"url": URLS["home_mypage_membership"], "keys": ["txt_mypage", "txt_mypage", "txt_gradeinfo"]},
]

def load_language_mapping(path="data/language.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def change_language(page: Page, lang_code: str):
    page.click('[data-testid=menu_ham]')
    page.wait_for_timeout(3000)
    page.click(f'[data-testid={LANGUAGE_TESTID[lang_code]}]')
    page.wait_for_timeout(5000)

def verify_translations(page: Page, texts: dict, lang_code: str, keys: list):
    for key in keys:
        locator = page.locator(f"[data-testid={key}]")
        locator.scroll_into_view_if_needed()
        actual = locator.inner_text().strip()
        expected = texts[key][lang_code]
        assert actual == expected, f"❌ {key}: {actual} != {expected}"

@pytest.mark.parametrize("lang_code", LANGUAGE_CODES)
@pytest.mark.parametrize("page_info", PAGES_TO_TEST)
def test_language_per_page(page: Page, lang_code: str, page_info: dict):
    texts = load_language_mapping()
    page.goto(URLS["home_main"])

    if lang_code != "ko":
        change_language(page, lang_code)

    page.goto(page_info["url"])
    verify_translations(page, texts, lang_code, page_info["keys"])
