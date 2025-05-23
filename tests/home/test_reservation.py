# 테스트 흐름
# 1. API를 통해 로그인 상태로 예약 화면 진입 
# 2. 테스트 일자 기준 20일 이후면 다음달 내에서 날짜 선택, 20일 이전이면 이번달 당일보다 미래 날짜 선택
# 3. 시간은 활성화된 시간들중 미래 시간 선택
# 4. 희망시술 내용 고정 "자동화 테스트 MM월 DD일 HH시 MM분 예약"
# 5. 약관 동의 후 완료 -> 예약 완료 페이지 진입
# 6. 예약 시 저장한 데이터 json 파일과 완료 화면 데이터 비교
import json
from config import URLS
from datetime import datetime, timedelta
from playwright.sync_api import Page, expect

def get_reservation_datetime():
    now = datetime.now()
    if now.day > 20:
        target_date = (now.replace(day=1) + timedelta(days=32)).replace(day=1)  # 다음 달 1일
        use_next_month = True
    else:
        target_date = now + timedelta(days=1)
        use_next_month = False

    return {
        "date": target_date.strftime("%Y-%m-%d"),
        "day": target_date.day,
        "month": target_date.month,
        "use_next_month": use_next_month,
    }

def get_available_time_button(page: Page):
    now = datetime.now()
    time_buttons = page.locator("[data-testid^='btn_time_']")
    count = time_buttons.count()
    for i in range(count):
        btn = time_buttons.nth(i)
        if btn.is_enabled():
            time_text = btn.inner_text()
            time_value = btn.get_attribute("data-testid").split("_")[-1]
            hour, minute = int(time_value[:2]), int(time_value[2:])
            time_obj = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if time_obj > now:
                return btn, f"{hour:02}:{minute:02}"
    raise Exception("선택 가능한 미래 시간이 없습니다")

def test_reservation(page: Page):
    # 예약 신청 페이지 진입 (로그인 토큰 context 포함 상태여야 함)
    page.goto(URLS["home_reservation"])

    reservation = get_reservation_datetime()

    # 캘린더 이동
    if reservation["use_next_month"]:
        page.click("[data-testid=btn_next]")

    # 날짜 선택
    page.click(f"[data-testid=btn_day__{reservation['day']:02}]")

    # 시간 선택
    btn, time_str = get_available_time_button(page)
    btn.click()

    # 희망 시술 입력
    memo = f"자동화 테스트 {reservation['month']:02}월 {reservation['day']:02}일 {time_str.replace(':', '시 ')}분 예약"
    page.fill("[data-testid=input_memo]", memo)

    # 약관 동의 및 예약
    page.click("[data-testid=btn_agree]")
    page.click("[data-testid=btn_confirm]")

    # 완료 문구 확인
    expect(page.locator("[data-testid=txt_complete]")).to_be_visible()

    # 예약 정보 저장
    reserved_info = {
        "name": "자동화고객",
        "birth": "1995-05-01",
        "gender": "여성",
        "phone": "010-1234-5678",
        "date": reservation["date"],
        "time": time_str,
        "memo": memo
    }

    with open("reservation.json", "w", encoding="utf-8") as f:
        json.dump(reserved_info, f, ensure_ascii=False, indent=2)

    # 예약 완료 화면 정보와 비교
    assert page.locator("[data-testid=result_name]").inner_text() == reserved_info["name"]
    assert page.locator("[data-testid=result_birth]").inner_text() == reserved_info["birth"]
    assert page.locator("[data-testid=result_gender]").inner_text() == reserved_info["gender"]
    assert page.locator("[data-testid=result_phone]").inner_text() == reserved_info["phone"]
    assert page.locator("[data-testid=result_date]").inner_text() == reserved_info["date"]
    assert page.locator("[data-testid=result_time]").inner_text() == reserved_info["time"]
    assert page.locator("[data-testid=result_memo]").inner_text() == reserved_info["memo"]
