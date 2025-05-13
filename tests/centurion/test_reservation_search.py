import json
import random
from playwright.sync_api import Page, expect
from helpers.reservation_utils import get_reservations_by_status

RESERVATION_FILE = "data/reservations.json"

def load_random_reservation():
    with open(RESERVATION_FILE, "r", encoding="utf-8") as f:
        reservations = json.load(f)
    return random.choice(reservations)

def test_search_and_reset_reservation_filters(page: Page):
    # 1. 랜덤 예약 정보 로드
    res = load_random_reservation()
    name = res["name"]
    birth = res["birth"]
    gender = res["gender"]
    phone = res.get["phone",""]
    email = res.get["email",""]
    date = res["datetime"].split(" / ")[0]
    status = res.get("status", "")  # 없을 경우 대비 기본값 ""

    # 2. 검색 필드 입력
    if status:
        page.get_by_test_id("search_status").select_option(label=status) 
    page.fill('[data-testid="search_name"]', name)
    page.fill('[data-testid="search_birth"]', birth)
    page.get_by_test_id("search_gender").select_option(label=gender)
    if phone:
        page.fill('[data-testid="search_phone"]', phone)
    if email:
        page.fill('[data-testid="search_email"]', email)
    page.fill('[data-testid="search_date"]', date)  # 날짜 필드의 ID 맞게 수정

    # 3. 검색 결과 확인 
    page.locator("body").click()
    expect(page.locator("table tbody tr")).to_have_count(1)

    # 4. 초기화 클릭
    page.click('[data-testid="btn_reset"]')

    # 5. 필드 초기화 상태 확인
    expect(page.locator('[data-testid="search_status"]')).to_have_value("")
    expect(page.locator('[data-testid="search_name"]')).to_have_attribute("value", "")
    expect(page.locator('[data-testid="search_birth"]')).to_have_attribute("value", "")
    expect(page.locator('[data-testid="search_gender"]')).to_have_value("")
    expect(page.locator('[data-testid="search_date"]')).to_have_attribute("value", "")

    if phone:
        expect(page.locator('[data-testid="search_phone"]')).to_have_attribute("value", "")
    if email:
        expect(page.locator('[data-testid="search_email"]')).to_have_attribute("value", "")

    # 6. 테이블 결과가 0건인지 확인
    expect(page.locator("table tbody tr")).to_have_count(0)

# 예약 상태에 따른 확정/취소 버튼 활성화 확인
def test_button_enable_by_status(page: Page):
    status_button_rules = {
        # "대기":  (True,  True),
        "확정":  (False, True),
        "취소":  (False, False),
    }

    for status, (accept_enabled, cancel_enabled) in status_button_rules.items():
        res_list = get_reservations_by_status(status)
        if not res_list:
            print(f"⚠️ 상태 '{status}' 예약 없음")
            continue

        target = res_list[0]
        name = target["name"]

        # 드롭다운 상태 선택 + 이름 입력 후 포커스 아웃
        page.get_by_test_id("search_status").select_option(label=status)
        page.fill('[data-testid="search_name"]', name)
        page.locator("body").click()

        row = page.locator("table tbody tr").first

        btn_accept = row.locator('[data-testid="btn_accept"]')
        btn_cancel = row.locator('[data-testid="btn_cancel"]')

        if accept_enabled:
            expect(btn_accept).to_be_enabled()
        else:
            expect(btn_accept).to_be_disabled()

        if cancel_enabled:
            expect(btn_cancel).to_be_enabled()
        else:
            expect(btn_cancel).to_be_disabled()
