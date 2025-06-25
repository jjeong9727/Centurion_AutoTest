# 멤버십 등급 관리 테스트 - 등록, 수정, 토글 포함
import random
from playwright.sync_api import Page, expect
from config import URLS
from helpers.customer_utils import cen_login

# ✅ 등급명 조건에 맞는 row 탐색 (페이지네이션 포함)
def find_row_across_pages(page: Page, match_fn) -> Page:
    while True:
        rows = page.locator("table tbody tr")
        row_count = rows.count()

        for i in range(row_count):
            row = rows.nth(i)
            cell = row.locator("td").nth(1)
            text = cell.inner_text().strip()
            if match_fn(text):
                return row

        # 다음 페이지 버튼 확인
        next_button = page.locator('[data-testid="page_next"]')
        if next_button.is_disabled():
            break
        next_button.click()
        page.wait_for_timeout(1500)

    return None

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

    # ✅ "등급명수정" 또는 "등급명최종수정" 등급명을 찾아 수정
    row = find_row_across_pages(page, lambda t: t in ["등급명수정", "등급명최종수정"])
    assert row, "❌ '등급명수정' 또는 '등급명최종수정' 등급명을 찾지 못했습니다."

    cell = row.locator("td").nth(1)
    original_text = cell.inner_text().strip()
    replacement_text = "등급명최종수정" if original_text == "등급명수정" else "등급명수정"

    cell.click()
    page.wait_for_timeout(500)
    input_field = cell.locator("input")
    input_field.fill(replacement_text)
    page.wait_for_timeout(500)
    input_field.press("Tab")
    page.wait_for_timeout(500)
    page.click('[data-testid="btn_confirm"]')
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_edit"]')).to_be_visible()
    page.wait_for_timeout(1000)

    # ✅ "자동화" 등급명 찾아 toggle 처리
    row = find_row_across_pages(page, lambda t: t == "자동화")
    assert row, "❌ '자동화' 등급명을 가진 행을 찾지 못했습니다."

    row.locator('[data-testid="btn_toggle"]').click()
    page.wait_for_timeout(2000)
    page.click('[data-testid="btn_cancel"]')
    page.wait_for_timeout(2000)
    row.locator('[data-testid="btn_toggle"]').click()
    page.wait_for_timeout(2000)
    page.click('[data-testid="btn_confirm"]')
    expect(page.locator('[data-testid="toast_using"]')).to_be_visible()
    page.wait_for_timeout(1000)
