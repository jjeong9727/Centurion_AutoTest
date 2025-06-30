# 상품 분류 Validation 
# 시술 관리 Validation 
# 상품 관리 Validation
# 상품 페이지 관리 Validation
import pytest
from playwright.sync_api import Page, expect
from helpers.customer_utils import cen_login  
from config import URLS

def test_category_duplicate_validation(page: Page):
    cen_login(page)  # ✅ 로그인
    page.goto(URLS["cen_category"])  # 카테고리 등록 페이지
    page.wait_for_timeout(3000)

    # ✅ [1] 대분류 등록 시도
    page.click('[data-testid="btn_add_category"]')  # 등록 진입 버튼
    page.fill('[data-testid="input_category_name"]', "자동화대분류")
    page.click('[data-testid="btn_complete"]')

    # ✅ 중복 토스트 확인
    expect(page.locator('[data-testid="toast_duplicate"]')).to_be_visible(timeout=3000)
    print("✅ 대분류 중복 토스트 확인 완료")

    # ✅ [2] 유형 변경 → 중분류로
    page.click('[data-testid="drop_category_type"]')  # 드롭다운 열기
    page.click('[data-testid="drop_item_sub"]')       # 중분류 선택 (예: 중분류 testid)

    # 이름 다시 입력
    page.fill('[data-testid="input_category_name"]', "자동화 중분류")
    page.click('[data-testid="btn_complete"]')

    # ✅ 중복 토스트 확인
    expect(page.locator('[data-testid="toast_duplicate"]')).to_be_visible(timeout=3000)
    print("✅ 중분류 중복 토스트 확인 완료")
