import pytest
from playwright.sync_api import expect
from config import URLS, MENU_META_login
from helpers.homepage_utils import switch_language_to_english
from helpers.auth_helper import login_with_token

def go_to_home_page(page, url):
    page.goto(url)
    page.wait_for_load_state('load')
    login_with_token(page)

def check_menu_visibility(page):
    menu_items = page.locator('[data-testid="header_menu"]')
    expect(menu_items).to_be_visible()

def scroll_to_footer(page):
    page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
    page.wait_for_timeout(1000)

def check_footer_elements(page):
    footer_ids = [
        "footer_instagram", "footer_branch", "footer_terms", "footer_policy", "footer_consent"
    ]
    for testid in footer_ids:
        expect(page.locator(f'[data-testid="{testid}"]')).to_be_visible()

def select_menu_and_verify_page(page, menu_key, device_profile):
    is_mobile = device_profile["is_mobile"]
    lang = "ko"
    prefix = f"/{lang}" + ("/m" if is_mobile else "")

    meta = MENU_META_login[menu_key]
    expected_url = f"{URLS['home_main']}{prefix}{meta['path']}"

    locator = page.locator(f'[data-testid="{meta["testid"]}"]')
    locator.wait_for(timeout=3000)
    locator.click(force=True)
    page.wait_for_timeout(3000)


    current_url = page.url
    assert expected_url in current_url, f"❌ URL mismatch: expected '{expected_url}', got '{current_url}'"

def click_float_button(page, is_mobile: bool):
    # 언어를 영어로 전환
    page.goto(URLS["home_main"])
    login_with_token(page)
    switch_language_to_english(page, is_mobile)

    # 예약 버튼 클릭 시 예약 화면 으로 이동
    if is_mobile:
        page.locator('[data-testid="btn_float"]').click()
        page.wait_for_timeout(1000)
        page.locator('[data-testid="float_reserve"]').click()
        page.wait_for_timeout(1000)

    else:
        page.locator('[data-testid="float_reserve"]').click()
        page.wait_for_timeout(1000)


    page.wait_for_load_state("load")
    assert "/reservation" in page.url, f"❌ 예약 페이지 아님: 2{page.url}"

    # 다시 홈 > 예약 버튼 선택
    page.goto(URLS["home_discover"])
    page.wait_for_timeout(1000)
    page.locator('[data-testid="btn_reservation"]').first.click()
    page.wait_for_timeout(2000)
    assert "/reservation" in page.url, f"❌ 예약 페이지 아님: {page.url}"

    # 상담 버튼도 확인 (PC는 바로 노출, 모바일은 float 다시 눌러야 함)
    page.goto(URLS["home_main"])
    page.wait_for_timeout(1000)

    if is_mobile:
        page.locator('[data-testid="btn_float"]').click()
        with page.expect_popup() as popup_info:
            page.locator('[data-testid="float_consult"]').click()
    else:
        with page.expect_popup() as popup_info:
            page.locator('[data-testid="float_consult"]').click()

    new_page = popup_info.value
    page.wait_for_timeout(2000)
    assert "api.whatsapp.com/send" in new_page.url, f"❌ 상담 URL 이동 실패: {new_page.url}"

def test_non_logged_in(page, device_profile):
    is_mobile = device_profile["is_mobile"]

    # 메인 페이지 진입
    go_to_home_page(page, URLS["home_main"])
    page.wait_for_timeout(2000)

    # 메뉴 열기
    page.locator('[data-testid="header_menu"]').click()
    page.wait_for_timeout(2000)
    check_menu_visibility(page)

    # 메뉴 테스트
    for idx, key in enumerate(MENU_META_login):
        select_menu_and_verify_page(page, key, device_profile)

        # ✅ 로그아웃 이후에는 푸터 체크 생략
        is_last_menu = (idx == len(MENU_META_login) - 1)
        if key == "logout" or is_last_menu:
            print("🚫 로그아웃 이후 푸터 생략")
        else:
            scroll_to_footer(page)
            check_footer_elements(page)

        # 화면 맨 위로 올리고 다음 메뉴를 위해 다시 메뉴 열기
        page.evaluate("window.scrollTo(0, 0);")
        page.wait_for_timeout(500)

        # 로그아웃 이후 메뉴가 사라졌을 수 있으므로 조건 분기
        if key != "logout":
            page.locator('[data-testid="header_menu"]').click()
            page.wait_for_timeout(2000)


    click_float_button(page, is_mobile)
    
