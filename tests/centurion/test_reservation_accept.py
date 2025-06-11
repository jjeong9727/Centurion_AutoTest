# 테스트 흐름
# 1. 홈페이지 예약(대기상태) -> 확정(일괄확정) / 취소(일괄취소), 확정 후 취소
# 2. CEN 예약 추가(확정상태) -> 취소

from playwright.sync_api import Page, expect
from helpers.reservation_utils import get_reservations_by_status, update_reservation_status
from config import URLS
from helpers.customer_utils import cen_login

def test_confirm_and_cancel_reservations(page: Page):
    # 홈페이지 예약 스크립트 작성 시 3건 이상 등록 필요
    # 대기 상태 예약 3건 불러오기
    pending = get_reservations_by_status("대기")
    if len(pending) < 3:
        print("❌ 대기 상태 예약이 3건 이상 필요합니다.")
        return

    for idx, flow in enumerate(["cancel", "confirm", "confirm_then_cancel"]):
        target = pending[idx]
        name = target["name"]

        cen_login(page) # 로그인
        # 상태 + 이름 검색
        page.goto(URLS["cen_reservation"])
        page.get_by_test_id("search_status").select_option(label="대기")
        page.fill('[data-testid="search_name"]', name)
        page.locator("body").click() # 포커스 아웃을 위한 다른 영역 클릭 
        row = page.locator("table tbody tr").first

        if flow == "cancel":
            row.locator('[data-testid="btn_cancel"]').click()
            page.click('[data-testid="btn_no"]')
            row.locator('[data-testid="btn_cancel"]').click()
            page.click('[data-testid="btn_yes"]')
            update_reservation_status(name, "취소")

        elif flow == "confirm":
            row.locator('[data-testid="btn_accept"]').click()
            page.click('[data-testid="btn_no"]')
            row.locator('[data-testid="btn_accept"]').click()
            page.click('[data-testid="btn_yes"]')
            update_reservation_status(name, "확정")

        elif flow == "confirm_then_cancel":
            row.locator('[data-testid="btn_accept"]').click()
            page.click('[data-testid="btn_no"]')
            row.locator('[data-testid="btn_accept"]').click()
            page.click('[data-testid="btn_yes"]')
            update_reservation_status(name, "확정")

            # 재검색 (상태가 이미 확정으로 변경됐기 때문에)
            page.get_by_test_id("search_status").select_option(label="확정")
            page.fill('[data-testid="search_name"]', name)
            page.locator("body").click()
            row = page.locator("table tbody tr").first

            row.locator('[data-testid="btn_cancel"]').click()
            page.click('[data-testid="btn_no"]')
            row.locator('[data-testid="btn_cancel"]').click()
            page.click('[data-testid="btn_yes"]')
            update_reservation_status(name, "취소")

# 일괄 확정을 위해 대기 상태 2개 이상 있어야 함
# 일괄 확정 / 일괄 수정 확인 
def test_bulk_confirm_and_cancel(page: Page):
    # 1. 가장 최근 대기 예약 4건 가져오기
    pending = get_reservations_by_status("대기")[-4:]  # 마지막 4건 기준
    if len(pending) < 4:
        print("❌ 대기 상태 예약 4건 필요")
        return

    first_batch = pending[:2]   # 확정 대상
    second_batch = pending[2:]  # 취소 대상

    # 2. 예약 상태 '대기'로 검색
    page.get_by_test_id("search_status").select_option(label="대기")
    page.click("body")

    rows = page.locator("table tbody tr")
    selected = 0
    for i in range(rows.count()):
        row = rows.nth(i)
        name = row.locator("td").nth(2).inner_text().strip()  # 이름
        if name in [r["name"] for r in first_batch]:
            row.locator("td").first.click()  # 1열 클릭 (체크)
            selected += 1
        if selected == 2:
            break

    # 3. 일괄 확정 버튼 클릭 + 확인
    page.click('[data-testid="btn_accept_bulk"]')
    page.click('[data-testid="btn_yes"]')

    # 4. 상태 업데이트 확인
    for res in first_batch:
        update_reservation_status(res["name"], "확정")

    # 5. 다시 대기 상태 검색 → 나머지 2건 체크
    page.get_by_test_id("search_status").select_option(label="대기")
    page.click("body")
    
    rows = page.locator("table tbody tr")
    selected = 0
    for i in range(rows.count()):
        row = rows.nth(i)
        name = row.locator("td").nth(2).inner_text().strip()
        if name in [r["name"] for r in second_batch]:
            row.locator("td").first.click()
            selected += 1
        if selected == 2:
            break

    # 6. 일괄 취소 버튼 클릭 + 확인
    page.click('[data-testid="btn_cancel_bulk"]')
    page.click('[data-testid="btn_yes"]')

    # 7. 상태 업데이트 확인
    for res in second_batch:
        update_reservation_status(res["name"], "취소")


