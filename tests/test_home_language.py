import pytest
import json
from playwright.sync_api import Page, expect
from config import URLS
from helpers.auth_helper import login_with_token


# 화면별 언어 데이터
screen_text_data = {
    "home_reservation": {
        "txt_date": {"ko": "예약 날짜", "en": "Date"},
        "txt_time": {"ko": "예약 시간", "en": "Time"},
        "txt_consent": {"ko": "[필수] 개인정보 수집 및 이용 동의", "en": "[Required] Consent to Collection and Use of Personal Information"},
        "btn_confirm": {"ko": "예약하기", "en": "Reservation"}
    },
    "home_privacy": {
        "txt_terms": {"ko": "개인정보 취급방침", "en": "Privacy Policy"}
    },
    "home_terms": {
        "txt_policy": {"ko": "사이트 이용약관", "en": "Terms of Use"}
    },
    "home_removal": {
        "txt_removal": {"ko": "제모 시술", "en": "Hair Removal"}
    },
    "home_lifting": {
        "txt_lifting": {"ko": "리프팅 시술", "en": "Lifting"}
    },
    "home_mypage_mem": {
        "txt_membership": {"ko": "멤버십 조회", "en": "Membership"},
        "txt_mypage": {"ko": "마이페이지", "en": "My Page"},
    },
    "home_mypage_profile": {
        "txt_profile": {"ko": "회원정보수정", "en": "Edit profile"},
        "txt_mypage": {"ko": "마이페이지", "en": "My Page"},
    },
    "home_mypage_history": {
        "txt_history": {"ko": "예약 내역 확인", "en": "Reservation History"},
        "txt_mypage": {"ko": "마이페이지", "en": "My Page"}
    },
    "home_mypage_mo": {
        "txt_mypage": {"ko": "마이페이지", "en": "My Page"},
        "menu_membership": {"ko": "멤버십 조회", "en": "Membership"},
        "menu_profile": {"ko": "회원정보수정", "en": "Edit profile"},
        "menu_history": {"ko": "예약 내역 확인", "en": "Reservation History"}
    }
}


def check_language_for_screen(page: Page, screen_data: dict, lang_code: str):
    page.wait_for_timeout(1000)
    for element_id, texts in screen_data.items():
        locator = page.locator(f'[data-testid="{element_id}"]')
        expect(locator).to_have_text(texts[lang_code], timeout=3000)


def get_device_profile(device_type: str) -> dict:
    with open("data/device_profile.json", "r", encoding="utf-8") as f:
        profiles = json.load(f)

    is_mobile = device_type == "mobile"

    matching_profiles = [
        profile for profile in profiles.values()
        if profile.get("is_mobile", False) == is_mobile
    ]

    if not matching_profiles:
        raise ValueError(f"❌ '{device_type}'에 해당하는 단말 정보가 없습니다.")
    return matching_profiles[0]


# 언어 전환 처리 (기기별 분기 포함)
def switch_language_to_english(page: Page, is_mobile: bool, url: str):
    try:
        if is_mobile:
            page.locator('[data-testid="header_menu"]').click()
            page.wait_for_timeout(1000)
            page.locator('[data-testid="language_eng"]').click()
            page.wait_for_timeout(1000)
            page.goto(url)
        else:
            page.locator('[data-testid="drop_language"]').click()
            page.wait_for_timeout(1000)
            page.locator('[data-testid="drop_language_eng"]').click()
        page.wait_for_timeout(2000)
    except Exception as e:
        raise RuntimeError(f"❌ 언어 변경 실패: {e}")
    
def switch_language_to_korean(page: Page, is_mobile: bool, url: str):
    try:
        if is_mobile:
            page.locator('[data-testid="header_menu"]').click()
            page.wait_for_timeout(1000)
            page.locator('[data-testid="language_kor"]').click()
            page.wait_for_timeout(1000)
            page.goto(url)
        else:
            page.locator('[data-testid="drop_language"]').click()
            page.wait_for_timeout(1000)
            page.locator('[data-testid="drop_language_kor"]').click()
        page.wait_for_timeout(2000)
    except Exception as e:
        raise RuntimeError(f"❌ 언어 변경 실패: {e}")


def check_language_and_switch(page: Page, screen_name: str, screen_data: dict, is_mobile: bool):
    login_with_token(page)
    url = URLS[f"home_{screen_name}"]
    page.goto(url)
    
    
    check_language_for_screen(page, screen_data, lang_code="ko")

    # 언어 전환 및 영어 텍스트 확인
    switch_language_to_english(page, is_mobile, url)
    check_language_for_screen(page, screen_data, lang_code="en")

    switch_language_to_korean(page, is_mobile, url)

def test_language_check_all(page: Page, device_profile):
    is_mobile = device_profile["is_mobile"]

    for screen_name, screen_data in screen_text_data.items():
        if is_mobile and screen_name in ["home_mypage_mem", "home_mypage_profile", "home_mypage_history"]:
            continue
        if not is_mobile and screen_name in ["home_mypage_mo"]:
            continue

        check_language_and_switch(page, screen_name.replace("home_", ""), screen_data, is_mobile)

