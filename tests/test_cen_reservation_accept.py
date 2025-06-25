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

    for idx, flow in enumerate(["cancel", "confirm"]): #"confirm_then_cancel"
        target = pending[idx]
        name = target["name"]

        cen_login(page) # 로그인
        # 상태 + 이름 검색
        page.goto(URLS["cen_reservation"])
        page.wait_for_timeout(3000)
        page.locator('[data-testid="search_status_trigger"]').click()
        page.get_by_role("option", name="대기").click()
        page.wait_for_timeout(1000)
        page.fill('[data-testid="search_name"]', name)
        page.wait_for_timeout(1000)
        page.locator("body").click() # 포커스 아웃을 위한 다른 영역 클릭 
        page.wait_for_timeout(1000)
        row = page.locator("table tbody tr").first

        if flow == "cancel":
            row.locator('[data-testid="btn_cancel"]').click()
            page.wait_for_timeout(1000)
            page.click('[data-testid="btn_no"]')
            page.wait_for_timeout(1000)
            row.locator('[data-testid="btn_cancel"]').click()
            page.wait_for_timeout(1000)
            page.click('[data-testid="btn_yes"]')
            page.wait_for_timeout(1000)
            update_reservation_status(name, "취소")

        elif flow == "confirm":
            row.locator('[data-testid="btn_accept"]').click()
            page.wait_for_timeout(1000)
            page.click('[data-testid="btn_no"]')
            page.wait_for_timeout(1000)
            row.locator('[data-testid="btn_accept"]').click()
            page.wait_for_timeout(1000)
            page.click('[data-testid="btn_yes"]')
            page.wait_for_timeout(1000)
            update_reservation_status(name, "확정")

        elif flow == "confirm_then_cancel":
            row.locator('[data-testid="btn_accept"]').click()
            page.wait_for_timeout(1000)
            page.click('[data-testid="btn_no"]')
            page.wait_for_timeout(1000)
            row.locator('[data-testid="btn_accept"]').click()
            page.wait_for_timeout(1000)
            page.click('[data-testid="btn_yes"]')
            page.wait_for_timeout(1000)
            update_reservation_status(name, "확정")

            # 재검색 (상태가 이미 확정으로 변경됐기 때문에)
            page.locator('[data-testid="search_status_trigger"]').click()
            page.get_by_role("option", name="확정").click()
            page.wait_for_timeout(1000)
            page.fill('[data-testid="search_name"]', name)
            page.wait_for_timeout(1000)
            page.locator("body").click()
            page.wait_for_timeout(1000)
            row = page.locator("table tbody tr").first

            row.locator('[data-testid="btn_cancel"]').click()
            page.wait_for_timeout(1000)
            page.click('[data-testid="btn_no"]')
            page.wait_for_timeout(1000)
            row.locator('[data-testid="btn_cancel"]').click()
            page.wait_for_timeout(1000)
            page.click('[data-testid="btn_yes"]')
            page.wait_for_timeout(1000)
            update_reservation_status(name, "취소")


