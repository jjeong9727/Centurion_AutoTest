import pytest
import json
from playwright.sync_api import Page, expect
from config import URLS
from helpers.auth_helper import login_with_token


# 화면별 언어 데이터
screen_text_data = {
    "home_main": {
        "btn_removal": {"ko": "제모 시술", "en": "Removal"},
        "btn_lifting": {"ko": "리프팅 시술", "en": "Lifting"}
    },
    "home_login": {
        "txt_login": {"ko": "로그인", "en": "LOGIN"},
        "btn_login": {"ko": "카카오로 시작하기", "en": "Sign in with Google"},
        "footer_branch": {"ko": "세라미크의원 강남", "en": "CERAMIQUE Clinic Gangnam"},
        "footer_terms": {"ko": "이용약관", "en": "Terms of Use"},
        "footer_policy": {"ko": "개인정보취급방침", "en": "Privacy Policy"},
        "float_reserve": {"ko": "예약", "en": "Book"},
        "float_consult": {"ko": "상담", "en": "Consult"}
    },
    "home_reservation": {
        "txt_date": {"ko": "예약 날짜", "en": "Date"},
        "txt_time": {"ko": "예약 시간", "en": "Time"},
        "txt_consent": {"ko": "[필수] 개인정보 수집 및 이용 동의", "en": "[Required] Consent to Collection and Use of Personal Information"},
        "btn_confirm": {"ko": "예약하기", "en": "Reservation"}
    },
    "home_privacy": {
        "txt_privacy": {"ko": "개인정보취급방침", "en": "Privacy Policy"}
    },
    "home_terms": {
        "txt_terms": {"ko": "이용약관", "en": "Terms of Use"}
    },
    "home_removal": {
        "txt_removal": {"ko": "제모 시술", "en": "Hair Removal"}
    },
    "home_lifting": {
        "txt_lifting": {"ko": "리프팅 시술", "en": "Lifting"}
    },
    "home_mypage_mem": {
        "txt_lifting": {"ko": "멤버십 조회", "en": "Membership"},
        "txt_mypage": {"ko": "마이페이지", "en": "My Page"},
    },
    "home_mypage_profile": {
        "txt_lifting": {"ko": "회원정보수정", "en": "Edit profile"},
        "txt_mypage": {"ko": "마이페이지", "en": "My Page"},
    },
    "home_mypage_history": {
        "txt_lifting": {"ko": "나의 예약 정보", "en": "My reservation"},
        "txt_mypage": {"ko": "마이페이지", "en": "My Page"}
    },
    "home_mypage_mo": {
        "txt_mypage": {"ko": "마이페이지", "en": "My Page"},
        "menu_membership": {"ko": "멤버십 조회", "en": "Membership"},
        "menu_profile": {"ko": "회원정보수정", "en": "Edit profile"},
        "menu_history": {"ko": "예약 내역 확인", "en": "Reservation History"}
    }
}


# 언어 텍스트 검증
def check_language_for_screen(page: Page, screen_data: dict, lang_code: str):
    page.wait_for_timeout(1000)
    for element_id, texts in screen_data.items():
        locator = page.locator(f'[data-testid="{element_id}"]')
        expect(locator).to_have_text(texts[lang_code], timeout=3000)


# 디바이스 설정 불러오기
def get_device_profile(device_type: str) -> dict:
    with open("data/device_profile.json", "r", encoding="utf-8") as f:
        profiles = json.load(f)

    is_mobile = device_type == "mobile"

    # 조건에 맞는 프로필 목록 필터링
    matching_profiles = [
        profile for profile in profiles.values()
        if profile.get("is_mobile", False) == is_mobile
    ]

    if not matching_profiles:
        raise ValueError(f"❌ '{device_type}'에 해당하는 단말 정보가 없습니다.")

    # 일단 첫 번째 matching 프로필 반환 (원하면 우선순위 로직 추가 가능)
    return matching_profiles[0]


# 언어 변경 테스트 수행 (한글 → 영어)
def check_language_and_switch(page: Page, screen_name: str, screen_data: dict):
    login_with_token(page)
    url = URLS[f"home_{screen_name}"]
    page.goto(url)
    check_language_for_screen(page, screen_data, lang_code="ko")

    # 언어 전환 (한국어 → 영어)
    try:
        page.click('[data-testid="btn_language"]')
        page.wait_for_timeout(1000)
        page.click('[data-testid="btn_language_en"]')
        page.wait_for_timeout(2000)
        check_language_for_screen(page, screen_data, lang_code="en")
    except Exception as e:
        raise RuntimeError(f"❌ 언어 전환 또는 영어 텍스트 확인 실패 - {screen_name}: {str(e)}")


@pytest.mark.parametrize("device_type", ["pc", "mobile"])
def test_language_check_all(page: Page, device_type: str):
    profile = get_device_profile(device_type)
    page.set_viewport_size(profile['viewport'])

    for screen_name, screen_data in screen_text_data.items():
        # 조건 분기 처리
        if device_type == "pc" and screen_name in ["home_mypage_mo"]:
            continue
        if device_type == "mobile" and screen_name in ["home_mypage_mem", "home_mypage_profile", "home_mypage_history"]:
            continue

        check_language_and_switch(page, screen_name.replace("home_", ""), screen_data)

