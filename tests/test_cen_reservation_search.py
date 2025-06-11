# 테스트 흐름
# 1. 검색 전 노출되는 항목의 개수 저장 
# 2. 검색 각 항목 입력 후 검색 결과 노출 확인(검색 결과 1건 되도록)
# 3. 초기화 버튼 선택 시 입력 필드 삭제 및 검색결과 초기화(검색 전 노출 항목의 개수)
# 4. 각 상태별 [확정/취소] 버튼 활성/비활성 상태 확인
import json
import random
from playwright.sync_api import Page, expect
from helpers.reservation_utils import get_reservations_by_status
from config import URLS
from helpers.customer_utils import cen_login

RESERVATION_FILE = "data/reservations.json"

def load_random_reservation():
    with open(RESERVATION_FILE, "r", encoding="utf-8") as f:
        reservations = json.load(f)
    return random.choice(reservations)

def test_search_and_reset_reservation_filters(page: Page):
    # 1. 초기 고객 리스트 수 저장
    initial_count = page.locator("table tbody tr").count()

    # 2. 랜덤 예약 정보 로드
    res = load_random_reservation()
    name = res["name"]
    birth = res["birth"]
    gender = res["gender"]
    phone = res.get("phone", "")
    email = res.get("email", "")
    date = res["datetime"].split(" / ")[0]
    status = res.get("status", "")

    cen_login(page) # 로그인
    page.goto(URLS["cen_reservation"])
    page.wait_for_timeout(3000)

    # 3. 검색 필드 입력
    if status:
        page.get_by_test_id("search_status").select_option(label=status)
        page.locator("body").click()
    page.fill('[data-testid="search_name"]', name)
    page.click("body")
    page.fill('[data-testid="search_birth"]', birth)
    page.click("body")
    page.get_by_test_id("search_gender").select_option(label=gender)
    if phone:
        page.fill('[data-testid="search_phone"]', phone)
        page.click("body")
    if email:
        page.fill('[data-testid="search_email"]', email)
        page.click("body")
    page.fill('[data-testid="search_date"]', date)
    page.click("body")

    # 4. 검색 결과 확인 (1건으로 제한되도록 설계됨)
    expect(page.locator("table tbody tr")).to_have_count(1)

    # 5. 초기화 버튼 클릭
    page.click('[data-testid="btn_reset"]')

    # 6. 입력 필드 초기화 상태 확인
    expect(page.locator('[data-testid="search_status"]')).to_have_value("")
    expect(page.locator('[data-testid="search_name"]')).to_have_attribute("value", "")
    expect(page.locator('[data-testid="search_birth"]')).to_have_attribute("value", "")
    expect(page.locator('[data-testid="search_gender"]')).to_have_value("")
    expect(page.locator('[data-testid="search_date"]')).to_have_attribute("value", "")
    if phone:
        expect(page.locator('[data-testid="search_phone"]')).to_have_attribute("value", "")
    if email:
        expect(page.locator('[data-testid="search_email"]')).to_have_attribute("value", "")

    # 7. 초기화 이후 초기 상태의 행 수와 일치하는지 확인
    expect(page.locator("table tbody tr")).to_have_count(initial_count)
    print(f"✅ 초기화 후 고객 리스트 정상 복원: {initial_count}건")

# 예약 상태별 확정/취소 버튼 활성화 체크 
def test_button_enable_by_status(page: Page):
    status_button_rules = {
        "대기": (True, True),
        "확정": (False, True),
        "취소": (False, False),
        "완료": (False, False)
    }
    status_editable_columns = {
        "대기": [8, 10],
        "확정": [8, 10],
        "취소": [10],
        "완료": [10]
    }

    for status, (accept_enabled, cancel_enabled) in status_button_rules.items():
        res_list = get_reservations_by_status(status)
        if not res_list:
            print(f"⚠️ 상태 '{status}' 예약 없음")
            continue

        target = res_list[0]
        name = target["name"]

        page.get_by_test_id("search_status").select_option(label=status)
        page.fill('[data-testid="search_name"]', name)
        page.click("body")
        row = page.locator("table tbody tr").first

        # 버튼 상태 확인
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

        # 열 수정 가능 여부 확인
        editable_cols = status_editable_columns.get(status, [])
        for col_index in [8, 10]:
            cell = row.locator(f"td:nth-of-type({col_index + 1})")
            has_button = cell.locator("button").count() > 0

            if col_index in editable_cols:
                assert has_button, f"❌ {status} 상태에서 {col_index}열은 수정 가능해야 함 (버튼 없음)"
                print(f"✅ {status} 상태에서 {col_index}열: 수정 가능 (버튼 있음)")
            else:
                assert not has_button, f"❌ {status} 상태에서 {col_index}열은 수정 불가해야 함 (버튼 있음)"
                print(f"✅ {status} 상태에서 {col_index}열: 수정 불가 (버튼 없음)")
