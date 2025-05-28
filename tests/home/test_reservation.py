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

# 예약 추가 공통 함수 
def run_reservation(page: Page, visitor_info: dict | None = None):
    reservation = get_reservation_datetime()
    page.goto(URLS["home_reservation"])

    if reservation["use_next_month"]:
        page.click("[data-testid=btn_next]")

    page.click(f"[data-testid=btn_day__{reservation['day']:02}]")

    btn, time_str = get_available_time_button(page)
    btn.click()

    # 방문자 정보 입력
    if visitor_info and visitor_info["name"] != ReservationInfo["booker"]["name"]:
        page.click("[data-testid=btn_visitor]")
        page.fill("[data-testid=input_name]", visitor_info["name"])
        page.click("[data-testid=drop_year_trigger]")
        page.locator(f"li:has-text('{visitor_info['birth'][:4]}')").click()
        page.click("[data-testid=drop_month_trigger]")
        page.locator(f"li:has-text('{int(visitor_info['birth'][5:7])}')").click()
        page.click("[data-testid=drop_day_trigger]")
        page.locator(f"li:has-text('{int(visitor_info['birth'][8:])}')").click()
        page.click(f"[data-testid=radio_{'male' if visitor_info['gender'] == '남자' else 'female'}]")
        page.fill("[data-testid=input_phone]", visitor_info["phone"])

    memo = f"자동화 테스트 {reservation['month']:02}월 {reservation['day']:02}일 {time_str.replace(':', '시 ')}분 예약"
    page.fill("[data-testid=input_memo]", memo)

    page.click("[data-testid=btn_agree]")
    page.click("[data-testid=btn_confirm]")

    expect(page.locator("[data-testid=txt_complete]")).to_be_visible()

    # 예약자 및 방문자 기준 정보 분리
    booker = ReservationInfo["booker"]
    visitor = visitor_info or booker

    # 파일 경로
    json_path = "reservation.json"

    # ✅ 기존 데이터 불러오기
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    # ✅ 저장용 이름
    if visitor["name"] != booker["name"]:
        name_for_save = f"{visitor['name']}({booker['name']})"
    else:
        name_for_save = booker["name"]

    # ✅ 생성 시각
    created_at = datetime.now().strftime("%Y.%m.%d %H시 %M분")

    # ✅ 저장할 예약 정보
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

    # ✅ 누적 저장
    existing_data.append(reserved_info)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)


    # ✅ 예약자 정보 검증 (예약 완료 화면)
    assert page.locator("[data-testid=result_name]").inner_text() == booker["name"]
    assert page.locator("[data-testid=result_birth]").inner_text() == booker["birth"]
    assert page.locator("[data-testid=result_gender]").inner_text() == booker["gender"]
    assert page.locator("[data-testid=result_phone]").inner_text() == booker["phone"]
    assert page.locator("[data-testid=result_date]").inner_text() == reservation["date"]
    assert page.locator("[data-testid=result_time]").inner_text() == time_str
    assert page.locator("[data-testid=result_memo]").inner_text() == memo

    # ✅ 방문자 정보 검증 (다른 경우에만 노출됨)
    if visitor["name"] != booker["name"]:
        assert page.locator("[data-testid=visitor_name]").inner_text() == visitor["name"]
        assert page.locator("[data-testid=visitor_birth]").inner_text() == visitor["birth"]
        assert page.locator("[data-testid=visitor_gender]").inner_text() == visitor["gender"]
        assert page.locator("[data-testid=visitor_phone]").inner_text() == visitor["phone"]
    else:
        assert page.locator("[data-testid=visitor_name]").count() == 0

# 예약자==방문자
def test_reservation_self(page: Page):
    run_reservation(page, visitor_info=ReservationInfo["booker"])

# 예약자!=방문자 
def test_reservation_for_visitor(page: Page):
    run_reservation(page, visitor_info=ReservationInfo["visitor"])
