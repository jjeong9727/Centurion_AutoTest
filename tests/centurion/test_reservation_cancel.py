from playwright.sync_api import Page, expect
from helpers.reservation_utils import get_reservations_by_status, update_reservation_status

def test_single_cancel_from_waiting(page: Page):
    waiting = get_reservations_by_status("대기")[-1:]
    if len(waiting) < 1:
        print("❌ 대기 상태 예약 1건 이상 필요")
        return

    single = waiting[0]

    page.get_by_test_id("search_status").select_option(label="대기")
    page.fill('[data-testid="search_name"]', single["name"])
    page.locator("body").click()

    row = page.locator("table tbody tr").first
    row.locator('[data-testid="btn_cancel"]').click()
    page.click('[data-testid="btn_no"]')
    row.locator('[data-testid="btn_cancel"]').click()
    page.click('[data-testid="btn_yes"]')

    page.get_by_test_id("search_status").select_option(label="취소")
    page.fill('[data-testid="search_name"]', single["name"])
    page.locator("body").click()

    row = page.locator("table tbody tr").first
    name_in_row = row.locator("td").nth(2).inner_text().strip()
    assert name_in_row == single["name"], "❌ 단일 취소 후 내역 미확인"
    update_reservation_status(single["name"], "취소")


def test_bulk_cancel_from_confirmed(page: Page):
    confirmed = get_reservations_by_status("확정")[-2:]
    if len(confirmed) < 2:
        print("❌ 확정 상태 예약 2건 필요")
        return

    bulk_1, bulk_2 = confirmed[0], confirmed[1]

    page.get_by_test_id("search_status").select_option(label="확정")
    page.locator("body").click()

    names_to_cancel = [bulk_1["name"], bulk_2["name"]]
    selected = 0
    rows = page.locator("table tbody tr")
    for i in range(rows.count()):
        row = rows.nth(i)
        name = row.locator("td").nth(2).inner_text().strip()
        if name in names_to_cancel:
            row.locator("td").first.click()
            selected += 1
        if selected == 2:
            break

    page.click('[data-testid="btn_cancel_bulk"]')
    page.click('[data-testid="btn_no"]')
    page.click('[data-testid="btn_cancel_bulk"]')
    page.click('[data-testid="btn_yes"]')

    page.get_by_test_id("search_status").select_option(label="취소")
    page.locator("body").click()

    rows = page.locator("table tbody tr")
    found = 0
    for i in range(rows.count()):
        row = rows.nth(i)
        name = row.locator("td").nth(2).inner_text().strip()
        if name in names_to_cancel:
            found += 1
    assert found == 2, "❌ 두 예약 모두 취소 상태로 전환되지 않음"

    update_reservation_status(bulk_1["name"], "취소")
    update_reservation_status(bulk_2["name"], "취소")
