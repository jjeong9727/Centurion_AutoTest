# 예약 상태별 확정/취소 버튼 활성화 체크
from playwright.sync_api import Page, expect
from config import URLS
from helpers.customer_utils import cen_login

def test_button_enable_by_status(page: Page):
    # 예약 상태에 따른 버튼 활성화 여부 규칙
    status_button_rules = {
        "대기": (True, True),
        "확정": (False, True),
        "취소": (False, False),
        "완료": (False, False)
    }

    for status, (accept_enabled, cancel_enabled) in status_button_rules.items():
        print(f"\n🔍 상태 '{status}' 검색 및 버튼 확인 중...")

        cen_login(page)
        page.goto(URLS["cen_reservation"])
        page.wait_for_timeout(2000)

        # 상태 선택
        page.locator('[data-testid="search_status_trigger"]').click()
        page.wait_for_timeout(500)
        page.get_by_role("option", name=status).click()
        page.wait_for_timeout(500)
        page.click("body")
        page.wait_for_timeout(1000)

        # 검색 결과 행이 있는지 확인
        rows = page.locator("table tbody tr")
        if rows.count() == 0:
            print(f"⚠️ 상태 '{status}'에 해당하는 예약이 없습니다.")
            continue

        row = rows.first
        action_cell = row.locator("td:nth-of-type(13)")
        btn_accept = action_cell.locator('[data-testid="btn_accept"]')
        btn_cancel = action_cell.locator('[data-testid="btn_cancel"]')

        # 확정 버튼 상태 확인
        if accept_enabled:
            expect(btn_accept).to_be_enabled()
            print(f"✅ '{status}' 상태 - 확정 버튼 활성화 확인")
        else:
            expect(btn_accept).to_be_disabled()
            print(f"✅ '{status}' 상태 - 확정 버튼 비활성화 확인")

        # 취소 버튼 상태 확인
        if cancel_enabled:
            expect(btn_cancel).to_be_enabled()
            print(f"✅ '{status}' 상태 - 취소 버튼 활성화 확인")
        else:
            expect(btn_cancel).to_be_disabled()
            print(f"✅ '{status}' 상태 - 취소 버튼 비활성화 확인")
