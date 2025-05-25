# 테스트 흐름
# 1. 사전예약 신청화면 진입
# 2. 각 입력 항목 데이터 입력 확인
from playwright.sync_api import Page, expect
import time
from config import URLS

def test_reservation_form(page: Page):
    page.goto(URLS["home_reservation"])

    # 이름
    page.get_by_placeholder("이름을 입력해 주세요.").fill("권정의")

    # 연락처
    page.get_by_placeholder("연락처를 입력해 주세요.").fill("01012345678")

    # 성별 - 여성 선택
    page.get_by_label("여성").click()

    # 생년월일 - 1997년 9월 27일 선택
    page.select_option("select[placeholder='년']", "1997")
    page.select_option("select[placeholder='월']", "09")
    page.select_option("select[placeholder='일']", "27")

    # 예약 날짜 드롭다운 열기 → 첫 항목 선택
    page.get_by_placeholder("예약 날짜를 선택해 주세요.").click()
    page.locator("ul >> li").first.click()

    # 예약 시간 드롭다운 열기 → 첫 항목 선택
    page.get_by_placeholder("예약 시간을 선택해 주세요.").click()
    page.locator("ul >> li").first.click()

    # 희망시술
    page.get_by_placeholder("희망하는 시술을 반드시 남겨주세요.").fill("사전예약 테스트")

    # 이메일
    page.get_by_placeholder("이메일 주소를 입력해 주세요.").fill("jekwon@madisolveai.com")

    # 입력 완료 버튼 클릭
    page.get_by_role("button", name="입력 완료").click()

    # 예약 완료 페이지 또는 메시지 확인
    expect(page).to_have_url(lambda url: "complete" in url or "success" in url)
    expect(page.locator("text=예약이 완료되었습니다")).to_be_visible()
