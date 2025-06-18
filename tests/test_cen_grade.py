# 멤버십 등급 관리
# 사용 중인 등급 비활성화 확인
# 등급명 / 메모 수정 후 반영 확인
# 등급명 수정 시 이름 중복 확인
# ON/OFF 상태에 따른 노출/미노출 확인
# 멤버십 등급 관리 테스트 - 등록, 수정, 토글까지 포함

import random
from playwright.sync_api import Page, expect
from config import URLS
from helpers.customer_utils import cen_login

def test_membership_register_and_toggle(page: Page):
    # ✅ 로그인 
    cen_login(page)

    # ✅ 등급 등록 팝업 진입 및 취소
    page.goto(URLS["cen_grade"])
    page.wait_for_timeout(3000)
    page.click('[data-testid="btn_register"]')
    page.wait_for_timeout(1000)
    expect(page.locator('[data-testid="btn_confirm"]')).to_be_disabled()

    page.click('[data-testid="btn_cancel"]')
    page.wait_for_timeout(2000)
    page.click('[data-testid="btn_register"]')
    page.wait_for_timeout(2000)

    # ✅ 등급명 입력 → 완료 버튼 활성화 확인
    page.fill('[data-testid="input_grade"]', "자동화")
    page.wait_for_timeout(1000)
    expect(page.locator('[data-testid="btn_confirm"]')).to_be_enabled()
    page.wait_for_timeout(1000)

    # ✅ 중복 등록 시도 → 중복 토스트 확인
    page.click('[data-testid="btn_confirm"]')
    page.wait_for_timeout(1000)
    expect(page.locator('[data-testid="toast_duplicate"]')).to_be_visible()
    page.wait_for_timeout(1000)

    # ✅ 팝업 닫기
    page.click('[data-testid="btn_cancel"]')
    page.wait_for_timeout(1000)

    # ✅ "등급명수정" 또는 "등급명최종수정" 수정 처리
    rows = page.locator("table tbody tr")
    row_count = rows.count()

    target_text = None
    replacement_text = None
    found = False

    for i in range(row_count):
        cell = rows.nth(i).locator("td").nth(1)
        text = cell.inner_text().strip()

        if text in ["등급명수정", "등급명최종수정"]:
            target_text = text
            replacement_text = "등급명최종수정" if text == "등급명수정" else "등급명수정"

            cell.click()
            page.wait_for_timeout(500)

            input_field = cell.locator("input")
            input_field.fill(replacement_text)
            page.wait_for_timeout(500)

            input_field.press("Tab")
            page.wait_for_timeout(500)

            page.click('[data-testid="btn_confirm"]')
            page.wait_for_timeout(1000)
            expect(page.locator('[data-testid="toast_edit"]')).to_be_visible()
            page.wait_for_timeout(2000)
            found = True
            break

    assert found, "❌ '등급명수정' 또는 '등급명최종수정' 등급명을 찾지 못했습니다."

    # ✅ "자동화" 등급명으로 다시 테이블 탐색 → toggle 테스트
    toggle_found = False

    for i in range(row_count):
        row = rows.nth(i)
        grade_name_cell = row.locator("td").nth(1)
        grade_name = grade_name_cell.inner_text().strip()

        if grade_name == "자동화":
            row.locator('[data-testid="btn_toggle"]').click()
            page.wait_for_timeout(2000)
            page.click('[data-testid="btn_cancel"]')
            page.wait_for_timeout(2000)
            row.locator('[data-testid="btn_toggle"]').click()
            page.wait_for_timeout(2000)
            page.click('[data-testid="btn_confirm"]')
            page.wait_for_timeout(500)
            expect(page.locator('[data-testid="toast_using"]')).to_be_visible()
            page.wait_for_timeout(1000)
            toggle_found = True
            break

    assert toggle_found, "❌ '자동화' 등급명을 가진 행을 찾지 못했습니다."
