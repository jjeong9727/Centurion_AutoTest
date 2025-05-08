import pytest
from playwright.sync_api import Page
from config import URLS
from helpers.homepage_utils import verify_popup_link

# 공통으로 보여야 하는 항목
COMMON_MENU_ITEMS = [
    "menu_discover",
    "menu_program",
    "menu_privilege",
    "language_kor",
    "language_eng"
]
# 비로그인 시 보여야 할 항목
GUEST_MENU_ITEMS = [
    "menu_login",
    "menu_register"
]
# 로그인 시 보여야 할 항목
LOGGEDIN_MENU_ITEMS = [
    "menu_logout",
    "menu_mypage"
]
# 공통 메뉴 확인 함수
def verify_menu_visibility(page: Page, expected_ids: list):
    for testid in expected_ids:
        locator = page.locator(f'[data-testid={testid}]')
        assert locator.is_visible(), f"❌ {testid} 메뉴가 표시되지 않음"

    # footer 인스타그램 이동 확인 
    page.goto(URLS["home_main"])
    verify_popup_link(page, "footer_instagram")


# 비로그인 상태 테스트
@pytest.mark.order(1)
def test_menu_guest(page: Page):
    page.goto(URLS["home_main"])
    page.click('[data-testid=menu_ham]')
    verify_menu_visibility(page, COMMON_MENU_ITEMS + GUEST_MENU_ITEMS)

# 로그인 상태 테스트 (토큰 직접 주입 방식)
@pytest.mark.order(2)
def test_menu_logged_in(page: Page):
    # 로그인 토큰 세팅
    page.context.add_cookies([
        {
            "name": "auth_token",
            "value": "YOUR_TOKEN_VALUE_HERE",  # 실제 발급된 토큰으로 교체
            "domain": "your-site.com",
            "path": "/",
            "httpOnly": True,
            "secure": True
        }
    ])
    page.goto(URLS["home_main"])
    page.click('[data-testid=menu_ham]')
    verify_menu_visibility(page, COMMON_MENU_ITEMS + LOGGEDIN_MENU_ITEMS)
