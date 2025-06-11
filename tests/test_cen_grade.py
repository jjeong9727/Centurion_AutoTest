# 멤버십 등급 관리
# 사용 중인 등급 비활성화 확인
# 등급명 / 메모 수정 후 반영 확인
# 등급명 수정 시 이름 중복 확인
# ON/OFF 상태에 따른 노출/미노출 확인

import random
from playwright.sync_api import Page, expect
from helpers.customer_utils import find_grade_row, cen_login
from config import URLS

def test_membership_register_and_toggle(page: Page):
    # 로그인 
    cen_login(page)

    # 1. 등급 등록 팝업 진입 및 취소
    page.goto(URLS["cen_grade"])
    page.click('[data-testid="btn_register"]')  # 등록 버튼
    expect(page.locator('[data-testid="btn_confirm"]')).to_be_disabled()  # 완료 버튼 비활성화 확인

    page.click('[data-testid="btn_cancel"]')  # 취소
    page.click('[data-testid="btn_register"]')  # 재진입

    # 2. 등급명 입력 → 완료 버튼 활성화 확인
    page.fill('[data-testid="input_grade"]', "자동화")
    expect(page.locator('[data-testid="btn_confirm"]')).to_be_enabled()

    # 3. 중복 등록 시도 → 중복 토스트 확인
    page.click('[data-testid="btn_confirm"]')
    expect(page.locator('[data-testid="toast_duplicate"]')).to_be_visible()

    # 4. 취소 버튼으로 팝업 닫기
    page.click('[data-testid="btn_cancel"]')

    # 5. 리스트에서 임의 행 선택 → 2열 등급명 수정
    rows = page.locator("table tbody tr")
    row_count = rows.count()
    target_row_index = random.randint(0, row_count - 1)
    second_cell = rows.nth(target_row_index).locator("td").nth(1)

    # 첫 번째 수정 → 취소
    original_text = second_cell.inner_text()
    second_cell.click()
    second_cell.fill(original_text + "수정")
    page.click("body")
    page.click('[data-testid="btn_cancel"]')  # 수정 안내 팝업 취소

    # 두 번째 수정 → 확인
    second_cell.click()
    second_cell.fill(original_text + "수정")
    second_cell.press("Tab")
    page.click('[data-testid="btn_confirm"]')  # 수정 안내 팝업 확인
    expect(page.locator('[data-testid="toast_edit"]')).to_be_visible()

    # 6. 리스트에서 "자동화" 등급 찾기
    grade_row = find_grade_row(page)
    assert grade_row, "❌ VIP 등급을 찾을 수 없습니다."

    # 이후 toggle 버튼 클릭
    grade_row.locator('[data-testid="btn_toggle"]').click()
    page.wait_for_timeout(2000)
    page.click('[data-testid="btn_cancel"]')  # 비활성화 안내 팝업 취소
    page.wait_for_timeout(2000)
    grade_row.locator('[data-testid="btn_toggle"]').click()
    page.wait_for_timeout(2000)
    page.click('[data-testid="btn_confirm"]')  # 비활성화 확인
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_using"]')).to_be_visible()
