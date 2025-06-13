# 테스트 흐름
# *** 예약자==방문자 / 예약자!=방문자 케이스 나누어 진행 
# 1. API를 통해 로그인 상태로 예약 화면 진입 
# 2. 테스트 일자 기준 20일 이후면 다음달 내에서 날짜 선택, 20일 이전이면 이번달 당일보다 미래 날짜 선택
# 3. 시간은 활성화된 시간들중 미래 시간 선택
# 4. 희망시술 내용 고정 "자동화 테스트 MM월 DD일 HH시 MM분 예약"
# 5. 약관 동의 후 완료 -> 예약 완료 페이지 진입
# 6. 예약 시 저장한 데이터와 완료 화면 데이터 비교
# 7. 예약 정보 json 파일로 저장 해서 CEN 테스트에 활용 
import json
from playwright.sync_api import Page, expect
from config import ReservationInfo, URLS
from helpers.homepage_utils import get_reservation_datetime, get_available_time_button
import os
from datetime import datetime
import time
from pathlib import Path
from helpers.auth_helper import login_with_token

DOWNLOAD_PATH = Path("downloads")  # 다운로드 경로

def run_reservation(page: Page, visitor_info: dict | None = None):
    page.goto(URLS["home_main"])
    login_with_token(page)
    page.goto(URLS["home_reservation"])
    page.wait_for_timeout(2000)

    # 방문자 정보 입력
    if visitor_info and visitor_info["name"] != ReservationInfo["booker"]["name"]:
        page.click("[data-testid=btn_visitor]")
        page.click("body")
        expect(page.locator("[data-testid=alert_name]")).to_be_visible()
        page.fill("[data-testid=input_name]", visitor_info["name"])

        # 생년월일 입력
        page.click("[data-testid=drop_year_trigger]")
        page.click("body")
        expect(page.locator("[data-testid=alert_birth]")).to_be_visible()


        page.click("[data-testid=drop_year_trigger]")
        page.locator(f"li:has-text('{visitor_info['birth'][:4]}')").click()

        page.click("[data-testid=drop_month_trigger]")
        page.click("body")
        expect(page.locator("[data-testid=alert_birth]")).to_be_visible()


        page.click("[data-testid=drop_month_trigger]")
        page.locator(f"li:has-text('{int(visitor_info['birth'][5:7])}')").click()

        page.click("[data-testid=drop_day_trigger]")
        page.click("body")
        expect(page.locator("[data-testid=alert_birth]")).to_be_visible()


        page.click("[data-testid=drop_day_trigger]")
        page.locator(f"li:has-text('{int(visitor_info['birth'][8:])}')").click()

        page.click(f"[data-testid=radio_{'male' if visitor_info['gender'] == '남자' else 'female'}]")

        # 전화번호 입력
        page.click("[data-testid=input_phone]")
        page.click("body")
        expect(page.locator("[data-testid=alert_phone]")).to_be_visible()


        page.fill("[data-testid=input_phone]", visitor_info["phone"])

        confirm_button_disabled = page.locator("[data-testid=btn_confirm]").is_disabled()
        assert confirm_button_disabled

    # 예약 날짜 및 시간 선택
    reservation = get_reservation_datetime(page)
    page.wait_for_timeout(1000)
    time_str = get_available_time_button(page)
    page.wait_for_timeout(1000)

    # 희망 시술 메모 입력
    page.click("[data-testid=input_memo]")
    page.click("body")
    expect(page.locator("[data-testid=alert_memo]")).to_be_visible()


    memo = f"자동화 테스트 {reservation['month']:02}월 {reservation['day']:02}일 {time_str.replace(':', '시 ')}분 예약"
    page.fill("[data-testid=input_memo]", memo)

    confirm_button_disabled = page.locator("[data-testid=btn_confirm]").is_disabled()
    assert confirm_button_disabled

    page.click("[data-testid=btn_agree]")
    confirm_button_enabled = page.locator("[data-testid=btn_confirm]").is_enabled()
    assert confirm_button_enabled

    page.click("[data-testid=btn_agree]")
    confirm_button_enabled = page.locator("[data-testid=btn_confirm]").is_enabled()
    assert confirm_button_enabled

    page.click("[data-testid=btn_confirm]")
    page.wait_for_url(URLS["home_complete"])
    expect(page.locator("[data-testid=txt_complete]")).to_be_visible()

    # 예약자 및 방문자 정보 분리
    booker = ReservationInfo["booker"]
    visitor = visitor_info or booker

    # JSON 저장
    json_path = "reservation.json"
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    name_for_save = visitor["name"] if visitor["name"] != booker["name"] else booker["name"]
    created_at = datetime.now().strftime("%Y.%m.%d / %H:%M")

    reserved_info = {
        "name": name_for_save,
        "birth": visitor["birth"],
        "gender": visitor["gender"],
        "phone": visitor["phone"],
        "date": reservation["date"],
        "time": time_str,
        "memo": memo,
        "created_at": created_at
    }

    existing_data.append(reserved_info)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)

    # 예약 완료 화면 검증
    assert page.locator("[data-testid=result_name]").inner_text() == booker["name"]
    assert page.locator("[data-testid=result_birth]").inner_text() == booker["birth"]
    assert page.locator("[data-testid=result_gender]").inner_text() == booker["gender"]
    assert page.locator("[data-testid=result_phone]").inner_text() == booker["phone"]
    assert page.locator("[data-testid=result_date]").inner_text() == reservation["date"]
    assert page.locator("[data-testid=result_time]").inner_text() == time_str
    assert page.locator("[data-testid=result_memo]").inner_text() == memo

    if visitor["name"] != booker["name"]:
        assert page.locator("[data-testid=visitor_name]").inner_text() == visitor["name"]
        assert page.locator("[data-testid=visitor_birth]").inner_text() == visitor["birth"]
        assert page.locator("[data-testid=visitor_gender]").inner_text() == visitor["gender"]
        assert page.locator("[data-testid=visitor_phone]").inner_text() == visitor["phone"]
    else:
        assert page.locator("[data-testid=visitor_name]").count() == 0

    # 미성년자 시술동의서 다운로드 확인
    download_button = page.locator("[data-testid=download_minors]")
    if visitor["birth"] and int(visitor["birth"][:4]) > 2004:
        assert download_button.is_visible()
        with page.expect_download() as download_info:
            download_button.click()
        download = download_info.value
        download_path = download.path()
        time.sleep(3)
        assert os.path.exists(download_path), f"❌ 다운로드된 파일이 존재하지 않습니다: {download_path}"
    else:
        assert download_button.count() == 0


# 예약자==방문자
def test_reservation_self(page: Page):
    run_reservation(page, visitor_info=ReservationInfo["booker"])

# 예약자!=방문자
def test_reservation_for_visitor(page: Page):
    run_reservation(page, visitor_info=ReservationInfo["visitor"])

# 예약자!=방문자(미성년자)
def test_reservation_for_minor(page: Page):
    run_reservation(page, visitor_info=ReservationInfo["minor"])