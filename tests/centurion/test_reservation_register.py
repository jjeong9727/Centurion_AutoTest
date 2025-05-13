import random
import string
from datetime import datetime, timedelta
from playwright.sync_api import Page, expect
from helpers.reservation_utils import save_reservation_to_json, verify_multiple_reservations_in_list

def generate_random_birth():
    year = random.randint(1990, 1999)
    month = random.randint(1, 12)
    day = random.randint(1, 28 if month == 2 else 30)
    return f"{year}{month:02}{day:02}"

def generate_random_memo(length=100):
    korean_chars = '가나다라마바사아자차카타파하서울부산한국자동화테스트'
    special_chars = '-.'
    charset = string.ascii_letters + string.digits + special_chars + korean_chars + ' '
    return ''.join(random.choices(charset, k=length))

def generate_unique_test_name(prefix="예약테스트"):
    timestamp = datetime.now().strftime("%m%d_%H%M%S")
    return f"{prefix}_{timestamp}"

def generate_random_phone():
    second = random.randint(1000, 9999)
    third = random.randint(1000, 9999)
    return f"010{second:04}{third:04}"

def register_reservation(page: Page):
    # 테스트 데이터
    name = generate_unique_test_name()
    birth = generate_random_birth()
    gender = random.choice(["남자", "여자"])
    phone = generate_random_phone()
    email = "tester@test.com"
    wrong_email = "tester"
    memo = generate_random_memo()

    tomorrow = datetime.today() + timedelta(days=1)
    day = str(tomorrow.day)
    date_testid = f"btn_day__{day}"

    # 1. 예약 추가 팝업 열기
    page.click('[data-testid="btn_register"]')

    # 2. 취소 → 팝업 닫힘 확인
    page.click('[data-testid="btn_no"]')
    # 다시 진입
    page.click('[data-testid="btn_register"]')

    # 3. 필드 입력
    page.fill('[data-testid="input_name"]', name)
    page.fill('[data-testid="input_birth"]', birth)
    page.get_by_test_id("drop_gender").select_option(label=gender)
    page.fill('[data-testid="input_phone"]', phone)

    # 잘못된 이메일 형식 입력 → 등록 시도
    page.fill('[data-testid="input_email"]', wrong_email)

    # 4. 예약일 선택
    page.click('[data-testid="input_date"]')
    page.click(f'[data-testid="{date_testid}"]')

    # 5. 시간 선택 (활성화된 것 중 첫 번째)
    time_button = page.locator('button[data-testid^="btn_time_"]:not(:disabled)').first
    time_testid = time_button.get_attribute("data-testid")  # 예: "btn_time_0930"
    selected_time = time_testid.replace("btn_time_", "")    # "0930"
    formatted_time = f"{selected_time[:2]}:{selected_time[2:]}"  # "09:30"
    time_button.click()

    # 예약일자 + 시간
    date_str = tomorrow.strftime("%Y.%m.%d")
    datetime_str = f"{date_str} / {formatted_time}"

    # 6. 메모 입력
    page.fill('[data-testid="input_memo"]', memo)

    # 7. 완료 클릭
    page.click('[data-testid="btn_yes"]')
    # 형식 오류 토스트 팝업 확인
    expect(page.locator('[data-testid="toast_invalid_email"]')).to_be_visible()
    
    # 올바른 이메일로 수정 후 완료
    page.fill('[data-testid="input_email"]', email)
    page.click('[data-testid="btn_yes"]')
    page.wait_for_timeout(500)
    # 8. 등록 완료 토스트 확인
    expect(page.locator('[data-testid="toast_register"]')).to_be_visible()

    reservation_data = {
        "name": name,
        "birth": birth,
        "gender": gender,
        "phone": phone,
        "email": email,
        "datetime": datetime_str,  # 최종 포맷으로 저장
        "status" : "확정"
    }
    save_reservation_to_json(reservation_data)


def test_register_three_reservations(page: Page):
    for _ in range(4): # 확정 상태 확인(1건) / 확정->취소(1건) / 확정->일괄 취소(2건)
        register_reservation(page)
    
    verify_multiple_reservations_in_list(page, count=4)
