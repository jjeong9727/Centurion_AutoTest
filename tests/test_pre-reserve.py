from playwright.sync_api import Page, expect
from config import URLS

def test_reservation_form(page: Page):
    page.goto(URLS["home_reservation"])

    # 이름 입력
    page.locator("[data-testid='name']").fill("테스트")

    # 연락처 입력
    page.locator("[data-testid='phone']").fill("01012345678")

    # 성별 - 여성 선택
    page.locator("[data-testid='gender-female']").click()

    # 생년월일 - 2000년 01월 01일 선택
    page.locator("[data-testid='birth-year-trigger']").click()
    year_option = page.locator("[data-testid='birth-year-content'] >> text=2000").first
    year_option.scroll_into_view_if_needed()
    year_option.click()

    page.locator("[data-testid='birth-month-trigger']").click()
    month_option = page.locator("[data-testid='birth-month-content'] >> text=01").first
    month_option.scroll_into_view_if_needed()
    month_option.click()

    page.locator("[data-testid='birth-day-trigger']").click()
    day_option = page.locator("[data-testid='birth-day-content'] >> text=01").first
    day_option.scroll_into_view_if_needed()
    day_option.click()

    # 예약 날짜 선택
    page.locator("[data-testid='reservation-date-trigger']").click()
    date_item = page.locator("[data-testid='reservation-date-content'] >> li").first
    date_item.scroll_into_view_if_needed()
    date_item.click()

    # 예약 시간 선택
    page.locator("[data-testid='reservation-time-trigger']").click()
    time_item = page.locator("[data-testid='reservation-time-content'] >> li").first
    time_item.scroll_into_view_if_needed()
    time_item.click()

    # 희망 시술
    page.locator("[data-testid='memo']").fill("사전예약 테스트입니다. 취소 부탁 드립니다.")

    # 이메일 입력
    page.locator("[data-testid='email']").fill("test@test.com")

    # 입력 완료 버튼 클릭
    page.locator("[data-testid='reservation-submit']").click()

    # 완료 페이지 URL 확인
    expect(page).to_have_url(URLS["home_reservation_complete"])
