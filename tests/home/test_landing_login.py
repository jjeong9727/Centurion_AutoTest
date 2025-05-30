# 화면 랜딩 확인 (로그인 상태)

import pytest
from playwright.sync_api import sync_playwright, expect
from config import URLS
from helpers.auth_helper import ensure_valid_token

# 메뉴 항목 및 예상 URL
def go_to_home_page(page, url, access_token=None):
    page.goto(url)
    if access_token:
        # 로그인된 상태로 테스트 진행, 토큰을 사용하여 로그인 처리
        page.add_cookie({
            'name': 'access_token',
            'value': access_token,
            'domain': 'example.com'  # 실제 도메인으로 변경 필요
        })
    page.wait_for_load_state('load')

def check_menu_visibility(page):
    menu_items = page.locator('[data-testid="header_menu"]')
    expect(menu_items).to_be_visible()

def scroll_to_footer(page):
    # 페이지 최하단으로 스크롤
    page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
    page.wait_for_timeout(1000)  # 잠시 기다려서 로딩 완료될 시간 확보

def check_footer_elements(page):
    # 푸터 및 관련 항목이 페이지에 표시되는지 확인
    footer_instagram = page.locator('[data-testid="footer_instagram"]')
    footer_kakao = page.locator('[data-testid="footer_kakao"]')
    footer_branch = page.locator('[data-testid="footer_branch"]')
    footer_terms = page.locator('[data-testid="footer_terms"]')
    footer_policy = page.locator('[data-testid="footer_policy"]')
    footer_consent = page.locator('[data-testid="footer_consent"]')

    # 각 항목들이 페이지에 보이는지 확인
    expect(footer_instagram).to_be_visible()
    expect(footer_kakao).to_be_visible()
    expect(footer_branch).to_be_visible()
    expect(footer_terms).to_be_visible()
    expect(footer_policy).to_be_visible()
    expect(footer_consent).to_be_visible()

def select_menu_and_verify_page(page, menu_item, expected_url):
    page.locator(f'[data-testid="menu_{menu_item}"]').click()  # 메뉴 항목을 클릭
    page.wait_for_load_state('load')  # 페이지가 완전히 로딩될 때까지 기다림
    expect(page.url()).toBe(expected_url)  # 현재 페이지 URL이 예상 URL과 일치하는지 확인

def click_float_button_and_reserve(page, device_type):
    if device_type == 'pc':
        # PC에서 바로 예약 버튼 클릭
        page.locator('[data-testid="float_reserve"]').click()
    elif device_type == 'mobile':
        # 모바일에서 플로팅 버튼을 한 번 클릭하여 예약 버튼 표시 후 클릭
        page.locator('[data-testid="btn_float"]').click()
        page.locator('[data-testid="float_reserve"]').click()

    # 예약 화면으로 이동했는지 URL로 확인
    page.wait_for_load_state('load')
    expect(page.url()).toBe(URLS["home_reserve"])

@pytest.mark.playwright
def test_logged_in_pc(page):
    # 로그인 상태로 메인 화면 진입
    access_token = ensure_valid_token()  # 로그인 토큰 확보
    go_to_home_page(page, URLS["home_main"], access_token)

    # 햄버거 메뉴 클릭하여 전체 메뉴 항목 확인
    page.locator('[data-testid="hamburger-menu"]').click()
    check_menu_visibility(page)

    # 로그인 상태에서 보여야 하는 메뉴 항목과 상태 확인
    menu_items = [
        ('discover', URLS["home_discover"]),
        ('removal', URLS["home_removal"]),
        ('lifting', URLS["home_lifting"]),
        ('privilege', URLS["home_privilege"]),
        ('mypage', URLS["home_mypage_pc"]),
        ('logout', URLS["home_main"]),
    ]

    for item, expected_url in menu_items:
        select_menu_and_verify_page(page, item, expected_url)

        # 햄버거 메뉴로 돌아가서 다음 메뉴 클릭을 위해 햄버거 메뉴 클릭
        page.locator('[data-testid="hamburger-menu"]').click()

    # 푸터 항목 확인 후 클릭하여 URL 확인
    scroll_to_footer(page)
    check_footer_elements(page)

    # 플로팅 버튼으로 예약 화면 진입 (PC)
    click_float_button_and_reserve(page, 'pc')


@pytest.mark.playwright
def test_logged_in_mobile(page):
    # 로그인 상태로 메인 화면 진입
    access_token = ensure_valid_token()  # 로그인 토큰 확보
    go_to_home_page(page, URLS["home_main"], access_token)

    # 햄버거 메뉴 클릭하여 전체 메뉴 항목 확인
    page.locator('[data-testid="hamburger-menu"]').click()
    check_menu_visibility(page)

    # 로그인 상태에서 보여야 하는 메뉴 항목과 상태 확인
    menu_items = [
        ('discover', URLS["home_discover"]),
        ('menu_removal', URLS["home_removal"]),
        ('menu_lifting', URLS["home_lifting"]),
        ('menu_privilege', URLS["home_privilege"]),
        ('menu_mypage', URLS["home_mypage_mo"]),
        ('menu_logout', URLS["home_main"]),
    ]

    for item, expected_url in menu_items:
        select_menu_and_verify_page(page, item, expected_url)

        # 햄버거 메뉴로 돌아가서 다음 메뉴 클릭을 위해 햄버거 메뉴 클릭
        page.locator('[data-testid="hamburger-menu"]').click()

    # 푸터 항목 확인 후 클릭하여 URL 확인
    scroll_to_footer(page)
    check_footer_elements(page)

    # 플로팅 버튼으로 예약 화면 진입 (모바일)
    click_float_button_and_reserve(page, 'mobile')
