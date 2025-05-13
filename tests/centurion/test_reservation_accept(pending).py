# 확정 / 취소 플로우
# 1. 대기 -> 확정(cen에서 예약 추가 시 바로 확정되므로 home 테스트와 연동 필요)
# 2. 대기 -> 취소(cen에서 예약 추가 시 바로 확정되므로 home 테스트와 연동 필요)
# 3. 확정 -> 취소
# 각 상태별 UI 확인 
# 1. 대기 상태 -> 확정 활성 / 취소 활성 (cen에서 예약 추가 시 바로 확정되므로 home 테스트와 연동 필요)
# 2. 확정 상태 -> 확정 비활성 / 취소 활성
# 3. 취소 상태 -> 확정 비활성 / 취소 비활성


from playwright.sync_api import Page, expect
from helpers.reservation_utils import get_reservations_by_status, update_reservation_status
# 예약 확정 / 예약 취소 확인
def test_confirm_and_cancel_reservations(page: Page):
    # 대기 상태 예약 3건 불러오기
    pending = get_reservations_by_status("대기")
    if len(pending) < 3:
        print("❌ 대기 상태 예약이 3건 이상 필요합니다.")
        return

    for idx, flow in enumerate(["cancel", "confirm", "confirm_then_cancel"]):
        target = pending[idx]
        name = target["name"]

        # 상태 + 이름 검색
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
    page.locator("body").click()

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
    page.locator("body").click()

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

# 예약 상태에 따른 확정/취소 버튼 활성화 확인
def test_button_enable_by_status(page: Page):
    status_button_rules = {
        "대기":  (True,  True),
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

