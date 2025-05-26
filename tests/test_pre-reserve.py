from playwright.sync_api import Page, expect
from config import URLS
import re

def test_reservation_form(page: Page):
    page.goto(URLS["home_reservation"])

    # 이름 입력
    page.locator("[data-testid='name']").fill("테스트")
    page.wait_for_timeout(1000)

    # 연락처 입력
    page.locator("[data-testid='phone']").fill("01012345678")
    page.wait_for_timeout(1000)

    # 성별 - 여성 선택
    page.locator('label[for="FEMALE"]').click()
    page.wait_for_timeout(1000)

    # 생년월일 - 2000년 01월 01일 선택
    # 생년월일: '년' 항목 열기 전 먼저 스크롤
    year_trigger = page.locator("[data-testid='birth-year-trigger']")
    year_trigger.evaluate("el => el.scrollIntoView({ block: 'center' })")
    year_trigger.click()

    # 연도 옵션 보이게 스크롤
    year_option = page.locator("[data-testid='birth-year-content'] >> text=2000").first
    year_option.evaluate("el => el.scrollIntoView({ block: 'center' })")
    year_option.click()

    # 월 선택
    page.locator("[data-testid='birth-month-trigger']").click()
    month_option = page.locator("[data-testid='birth-month-content'] >> text=01").first
    month_option.evaluate("el => el.scrollIntoView({ block: 'center' })")
    month_option.click(force=True)

    # 일 선택
    page.locator("[data-testid='birth-day-trigger']").click()
    day_option = page.locator("[data-testid='birth-day-content'] >> text=01").first
    day_option.evaluate("el => el.scrollIntoView({ block: 'center' })")
    day_option.click(force=True)

    # 희망 시술
    page.locator("[data-testid='memo']").click()
    page.locator("[data-testid='memo']").fill("사전예약 테스트입니다. 취소 부탁 드립니다.")
    page.wait_for_timeout(1000)

    # 이메일 입력
    page.locator("[data-testid='email']").fill("test@test.com")
    page.wait_for_timeout(1000)

    # 예약 날짜 선택
    page.locator("[data-testid='reservation-date-trigger']").click()
    page.wait_for_timeout(1000)
    date_select = page.locator("select[aria-hidden='true']").nth(3)
    last_date_value = date_select.locator("option").last.get_attribute("value")
    date_select.select_option(last_date_value)
    page.mouse.click(0, 0)
    page.wait_for_timeout(1000)

    # 예약 시간 선택
    page.locator("[data-testid='reservation-time-trigger']").click()
    page.wait_for_timeout(3000)
    time_select = page.locator("select[aria-hidden='true']").nth(4)
    last_time_value = time_select.locator("option").last.get_attribute("value")
    time_select.select_option(last_time_value)
    page.mouse.click(0, 0)
    page.wait_for_timeout(1000)



    #입력 완료 버튼 클릭
    page.locator("[data-testid='reservation-submit']").click()
    page.wait_for_timeout(3000)

    # 완료 페이지 URL 확인 (부분 일치)
    expect(page).to_have_url(re.compile(rf"{URLS['home_reservation_complete']}.*"))
    page.wait_for_timeout(1000)

    # 텍스트 포함 여부 확인
    expect(page.locator("body")).to_contain_text("예약이 완료되었습니다")
    expect(page.locator("body")).to_contain_text("사전예약 테스트입니다. 취소 부탁 드립니다.")
