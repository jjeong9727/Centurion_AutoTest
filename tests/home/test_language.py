import pytest
from playwright.sync_api import sync_playwright, expect
import json
from config import URLS  

# 화면별 언어 텍스트 비교 함수
def check_language_for_screen(page, screen_data, device_type):
    # 페이지 로딩 대기
    page.wait_for_load_state('load')

    # 화면에 해당하는 테스트 아이디로 요소를 찾아 텍스트가 일치하는지 확인
    for element_id, texts in screen_data.items():
        element = page.locator(f'[data-testid="{element_id}"]')

        # 한국어 텍스트 확인
        expect(element).to_have_text(texts['ko'], timeout=3000)

        # 영어 텍스트 확인
        expect(element).to_have_text(texts['en'], timeout=3000)

# 단말 정보를 불러오는 함수 (PC와 Mobile 구분)
def get_device_profile(device_type):
    with open('data/device_profile.json', 'r') as f:
        device_profile = json.load(f)
    return device_profile[device_type]

# 화면별 언어 데이터 (중복 제거)
screen_text_data = {
    "main": {
        "btn_removal": {"ko": "제모 시술", "en": "Removal"},
        "btn_lifting": {"ko": "리프팅 시술", "en": "Lifting"}
    },
    "login": {
        "txt_login": {"ko": "로그인", "en": "LOGIN"},
        "btn_login": {"ko": "카카오로 시작하기", "en": "Sign in with Google"},
        "footer_branch": {"ko": "세라미크의원 강남", "en": "CERAMIQUE Clinic Gangnam"},
        "footer_terms": {"ko": "이용약관", "en": "Terms of Use"},
        "footer_policy": {"ko": "개인정보취급방침", "en": "Privacy Policy"},
        "float_reserve": {"ko": "예약", "en": "Book"},
        "float_consult": {"ko": "상담", "en": "Consult"}
    },
    "reservation": {
        "txt_date": {"ko": "예약 날짜", "en": "Date"},
        "txt_time": {"ko": "예약 시간", "en": "Time"},
        "txt_consent": {"ko": "[필수] 개인정보 수집 및 이용 동의", "en": "[Required] Consent to Collection and Use of Personal Information"},
        "btn_confirm": {"ko": "예약하기", "en": "Reservation"}
    },
    "policy": {
        "txt_policy": {"ko": "개인정보취급방침", "en": "Privacy Policy"},
        "txt_terms": {"ko": "이용약관", "en": "Terms of Use"}
    },
    "removal": {
        "txt_removal": {"ko": "제모 시술", "en": "Hair Removal"}
    },
    "lifting": {
        "txt_lifting": {"ko": "리프팅 시술", "en": "Lifting"}
    },
    "mypage": {
        "txt_mypage": {"ko": "마이페이지", "en": "My Page"},
        "menu_membership": {"ko": "멤버십 조회", "en": "Membership"},
        "menu_profile": {"ko": "회원정보수정", "en": "Edit profile"},
        "menu_history": {"ko": "예약 내역 확인", "en": "Reservation History"}
    }
}

# 화면별 언어 확인 및 페이지 진입 함수
def check_language_for_screen_and_navigate(page, screen_name, screen_data):
    # 각 화면 URL로 이동
    url = URLS[f"home_{screen_name}"]
    page.goto(url)
    
    # 텍스트 비교
    check_language_for_screen(page, screen_data, screen_name)

@pytest.mark.playwright
def test_language_check_pc(page):
    # PC 단말 정보 불러오기
    device_profile = get_device_profile("pc")
    page.set_viewport_size(device_profile['viewport'])

    # 각 화면에 대해 언어 확인 및 페이지 진입
    for screen_name, screen_data in screen_text_data.items():
        check_language_for_screen_and_navigate(page, screen_name, screen_data)


@pytest.mark.playwright
def test_language_check_mobile(page):
    # Mobile 단말 정보 불러오기
    device_profile = get_device_profile("mobile")
    page.set_viewport_size(device_profile['viewport'])

    # 각 화면에 대해 언어 확인 및 페이지 진입
    for screen_name, screen_data in screen_text_data.items():
        check_language_for_screen_and_navigate(page, screen_name, screen_data)
