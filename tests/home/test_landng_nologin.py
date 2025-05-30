# 화면 랜딩 확인 (비로그인 상태)

import pytest
from playwright.sync_api import Page
from config import URLS
from playwright.sync_api import expect
from helpers.auth_helper import ensure_valid_token

# 메뉴 항목 및 예상 URL
def go_to_home_page(page, url):
    page.goto(url)
    page.wait_for_load_state('load')

def check_menu_visibility(page):
    menu_items = page.locator('[data-testid="header_menu"]')
    expect(menu_items).to_be_visible()

def scroll_to_footer(page):
    # 페이지 최하단으로 스크롤
    page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
    page.wait_for_timeout(1000)  

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
    # 메뉴를 클릭하고 페이지로 이동 후 URL이 올바른지 확인
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

    # 로그인 화면으로 이동했는지 URL로 확인
    page.wait_for_load_state('load')
    expect(page.url()).toBe([URLS["home_login"]])

    # Discover -> 예약하러가기 버튼으로 이동 확인
    page.goto(URLS["home_discover"])
    page.locator('[data-testid="btn_reservation"]').first.click()
    page.wait_for_timeout(2000)
    expect(page.url()).toBe([URLS["home_login"]])


@pytest.mark.playwright
def test_non_logged_in_pc(page, access_token):
    # 비로그인 상태로 메인 화면 진입
    go_to_home_page(page, URLS["home_main)"])

    # 햄버거 메뉴 클릭하여 전체 메뉴 항목 확인
    page.locator('[data-testid="hamburger-menu"]').click()
    check_menu_visibility(page)

    # 비로그인 상태에서 보여야 하는 메뉴 항목과 상태 확인
    menu_items = [
        ('discover', URLS["home_discover"]),
        ('removal', URLS["home_removal"]),
        ('lifting', URLS["home_lifting"]),
        ('privilege', URLS["home_privilege"]),
        ('login', URLS["home_login"])
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
def test_non_logged_in_mobile(page, access_token):
    # 비로그인 상태로 메인 화면 진입
    go_to_home_page(page, URLS["home_main"])

    # 햄버거 메뉴 클릭하여 전체 메뉴 항목 확인
    page.locator('[data-testid="hamburger-menu"]').click()
    check_menu_visibility(page)

    # 비로그인 상태에서 보여야 하는 메뉴 항목과 상태 확인
    menu_items = [
        ('discover', URLS["home_discover"]),
        ('removal', URLS["home_removal"]),
        ('lifting', URLS["home_lifting"]),
        ('privilege', URLS["home_privilege"]),
        ('login', URLS["home_login"])
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