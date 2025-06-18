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
from pathlib import Path

RESERVATION_FILE = Path("data/reservation.json")

def load_random_reservation():
    with open(RESERVATION_FILE, "r", encoding="utf-8") as f:
        reservations = json.load(f)
    return random.choice(reservations)

def test_search_and_reset_reservation_filters(page: Page):

    # 2. 랜덤 예약 정보 로드
    res = load_random_reservation()
    name = res["name"]
    birth = res["birth"]
    gender = res["gender"]
    phone = res.get("phone", "")
    email = res.get("email", "")
    date = res["date"] 
    status = res.get("status", "")

    cen_login(page) # 로그인
    page.goto(URLS["cen_reservation"])
    page.wait_for_timeout(3000)
    # 초기 카운트 저장
    initial_count = page.locator("table tbody tr").count()


    # 3. 검색 필드 입력
    if status:
        page.locator('[data-testid="search_status_trigger"]').click()
        page.wait_for_timeout(1000)
        page.get_by_role("option", name=status).click()
        page.wait_for_timeout(1000)
        page.locator("body").click()
        page.wait_for_timeout(1000)

    page.fill('[data-testid="search_name"]', name)
    page.wait_for_timeout(1000)
    page.click("body")
    page.wait_for_timeout(1000)
    page.fill('[data-testid="search_birth"]', birth)
    page.wait_for_timeout(1000)
    page.click("body")
    page.wait_for_timeout(1000)
    page.locator('[data-testid="search_gender_trigger"]').click()
    page.wait_for_timeout(1000)
    page.get_by_role("option", name=gender).click()
    if phone:
        page.fill('[data-testid="search_phone"]', phone)
        page.wait_for_timeout(1000)
        page.click("body")
        page.wait_for_timeout(1000)
    if email:
        page.fill('[data-testid="search_email"]', email)
        page.wait_for_timeout(1000)
        page.click("body")
        page.wait_for_timeout(1000)

    # 4. 검색 결과 확인 (1건으로 제한되도록 설계됨)
    row = page.locator("table tbody tr").first

    # 생년월일 비교 (YYYY-MM-DD → YYYY.MM.DD)
    birth_cell = row.locator("td").nth(3)
    expect(birth_cell).to_contain_text(birth.replace("-", "."))

    # 전화번호 비교
    if phone:
        phone_cell = row.locator("td").nth(5)
        expect(phone_cell).to_contain_text(phone)

    print("✅ 첫 번째 행에서 생년월일 및 전화번호 정상 확인")
    # 5. 초기화 버튼 클릭
    page.click('[data-testid="btn_reset_filter"]')
    page.wait_for_timeout(1000)

    # 6. 입력 필드 초기화 상태 확인
    expect(page.locator('[data-testid="search_status_trigger"]')).to_have_text("상태 선택")
    expect(page.locator('[data-testid="search_name"]')).to_have_attribute("value", "")
    expect(page.locator('[data-testid="search_birth"]')).to_have_attribute("value", "")
    expect(page.locator('[data-testid="search_gender_trigger"]')).to_have_text("성별 선택")
    if phone:
        expect(page.locator('[data-testid="search_phone"]')).to_have_attribute("value", "")
    if email:
        expect(page.locator('[data-testid="search_email"]')).to_have_attribute("value", "")

    # 7. 초기화 이후 초기 상태의 행 수와 일치하는지 확인
    expect(page.locator("table tbody tr")).to_have_count(initial_count)
    print(f"✅ 초기화 후 고객 리스트 정상 복원: {initial_count}건")

# # 예약 상태별 확정/취소 버튼 활성화 체크 
# def test_button_enable_by_status(page: Page):
#     status_button_rules = {
#         "대기": (True, True),
#         "확정": (False, True),
#         "취소": (False, False),
#         "완료": (False, False)
#     }

#     for status, (accept_enabled, cancel_enabled) in status_button_rules.items():
#         res_list = get_reservations_by_status(status)
#         if not res_list:
#             print(f"⚠️ 상태 '{status}' 예약 없음")
#             continue

#         target = res_list[0]
#         name = target["name"]
        
#         cen_login(page)
#         page.goto(URLS["cen_reservation"])
#         page.wait_for_timeout(2000)

#         # 상태 및 이름으로 검색
#         page.locator('[data-testid="search_status_trigger"]').click()
#         page.wait_for_timeout(500)
#         page.get_by_role("option", name=status).click()
#         page.wait_for_timeout(500)
#         page.fill('[data-testid="search_name"]', name)
#         page.click("body")
#         page.wait_for_timeout(1000)

#         row = page.locator("table tbody tr").first

#         # 버튼 상태 확인
#         action_cell = row.locator("td:nth-of-type(13)")
#         btn_accept = action_cell.locator('[data-testid="btn_accept"]')
#         btn_cancel = action_cell.locator('[data-testid="btn_cancel"]')

#         if accept_enabled:
#             expect(btn_accept).to_be_enabled()
#             print(f"✅ '{status}' 상태 - 확정 버튼 활성화 확인")
#         else:
#             expect(btn_accept).to_be_disabled()
#             print(f"✅ '{status}' 상태 - 확정 버튼 비활성화 확인")

#         if cancel_enabled:
#             expect(btn_cancel).to_be_enabled()
#             print(f"✅ '{status}' 상태 - 취소 버튼 활성화 확인")
#         else:
#             expect(btn_cancel).to_be_disabled()
#             print(f"✅ '{status}' 상태 - 취소 버튼 비활성화 확인")
