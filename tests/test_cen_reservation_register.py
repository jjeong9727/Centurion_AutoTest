# 테스트 흐름
# 1. 예약 정보 생성 후 예약 4건 추가
# 2. 이름을 기준으로 예약 내역에서 예약 4건 확인

import random
import string
from datetime import datetime, timedelta
from playwright.sync_api import Page, expect
from helpers.reservation_utils import save_reservation_to_json, verify_multiple_reservations_in_list
from helpers.homepage_utils import get_available_time_button, get_reservation_datetime
from config import URLS
from helpers.customer_utils import cen_login

def generate_random_memo(length=100):
    korean_chars = '가나다라마바사아자차카타파하서울부산한국자동화테스트'
    special_chars = '-.'
    charset = string.ascii_letters + string.digits + special_chars + korean_chars + ' '
    return ''.join(random.choices(charset, k=length))

def register_reservation(page: Page):
    # 테스트 데이터
    name = "자동화예약테스트"
    birth = "1988.08.08"
    gender = "여자"
    phone = "010-0011-1234"
    memo = generate_random_memo()

    cen_login(page) # 로그인

    # 1. 예약 추가 팝업 열기
    page.goto(URLS["cen_reservation"])
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_register"]')
    page.wait_for_timeout(1000)

    # 2. 취소 → 팝업 닫힘 확인
    page.click('[data-testid="btn_no"]')
    page.wait_for_timeout(1000)
    # 다시 진입
    page.click('[data-testid="btn_register"]')
    page.wait_for_timeout(1000)

    # 3. 이름 필드 입력
    page.click('[data-testid="search_customer_trigger"]')
    page.wait_for_timeout(1000)
    page.fill('[data-testid="search_customer_search"]', name)
    page.wait_for_timeout(1000)
    page.locator('[data-testid="search_customer_item"]', has_text=name).first.click()
    page.wait_for_timeout(2000)

    # 4. 예약일 선택
    page.click('[data-testid="input_date"]')
    page.wait_for_timeout(1000)
    reservation = get_reservation_datetime(page)
    page.wait_for_timeout(3000)
    raw_date = reservation["date"]  # "YYYY-MM-DD"
    date = raw_date.replace("-", ".")  # "YYYY.MM.DD"

    # 5. 시간 선택 
    time = get_available_time_button(page)

    # 예약일자 + 시간
    date_str = date
    datetime_str = f"{date_str} / {time}"

    # 6. 메모 입력
    page.fill('[data-testid="input_memo"]', memo)
    page.wait_for_timeout(1000)

    # 7. 완료 클릭
    page.click('[data-testid="btn_yes"]')
    page.wait_for_timeout(500)

    # 8. 등록 완료 토스트 확인
    expect(page.locator('[data-testid="toast_register"]')).to_be_visible()
    page.wait_for_timeout(1000)
    

    # reservation_data = {
    #     "name": name,
    #     "birth": birth,
    #     "gender": gender,
    #     "phone": phone,
    #     "email": email,
    #     "datetime": datetime_str,  # 최종 포맷으로 저장
    #     "status" : "확정",
    #     "memo" : "memo"
    # }
    # save_reservation_to_json(reservation_data)


def test_register_reservation(page: Page):
    register_reservation(page)
    # verify_multiple_reservations_in_list(page, count=1)
    