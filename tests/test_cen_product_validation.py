# 상품 분류 Validation 
# 시술 관리 Validation 
# 상품 관리 Validation
# 상품 페이지 관리 Validation
import pytest
import json
from playwright.sync_api import Page, expect
from helpers.customer_utils import cen_login  
from helpers.product_utils import check_unsave_popup
from config import URLS

EDIT_JSON_PATH = "data/prd_category.json"
with open(EDIT_JSON_PATH, "r", encoding="utf-8") as f:
    edit_data = json.load(f)

current_main = edit_data["main"]
current_sub = edit_data["sub"]
edit_main = "대분류수정테스트" if current_main == "대분류수정" else "대분류수정"
edit_sub = "중분류수정테스트" if current_sub == "중분류수정" else "중분류수정"
ctg_main = "자동화대분류"
ctg_sub = "자동화중분류"

# ✅상품 분류 관리 
def test_category_duplicate_validation(page: Page):
    cen_login(page) 
    page.goto(URLS["cen_category"])
    page.wait_for_timeout(3000)

    # 대분류 등록 화면 중복 토스트 확인 
    page.click('[data-testid="btn_register"]')  
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_category_name"]', ctg_main)
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_complete"]')
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_duplicate_main"]')).to_be_visible(timeout=3000)
    print("✅ 대분류 중복 토스트 확인 완료")
    page.wait_for_timeout(1000)

    # 중분류 등록 화면 중복 토스트 확인 
    page.click('[data-testid="drop_type_trigger"]')  
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_type_item"]', has_text="중분류").click()    
    page.wait_for_timeout(1000)
    
    page.fill('[data-testid="input_category_name"]', ctg_sub)
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_complete"]')
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_duplicate"]')).to_be_visible(timeout=3000)
    print("✅ 중분류 중복 토스트 확인 완료")
    page.wait_for_timeout(1000)

    # 등록 화면 이탈 팝업 확인 
    check_unsave_popup(page)
    expect(page).to_have_url(URLS["cen_category"], timeout=3000)
    page.wait_for_timeout(1000)    

    # 수정 화면에서 중복 확인 
    page.fill('[data-testid="search_name"]', current_main)
    page.locator("body").click(position={"x": 10, "y": 10})

    row = page.locator("table tbody tr").first
    row.locator("td").last.click()
    page.wait_for_timeout(2000)
    page.locator('[data-testid="btn_review"]').click()
    page.wait_for_timeout(1000)

    page.locator('[data-testid="btn_edit"]').click()
    page.wait_for_timeout(1000)
    page.fill('[data-testid="search_name"]', edit_main)
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_complete"]')
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_duplicate_main"]')).to_be_visible(timeout=3000)
    print("✅ 대분류 중복 토스트 확인 완료")
    page.wait_for_timeout(1000)

    # 수정 화면 이탈 팝업 확인 후 리스트로 복귀 
    page.click('[data-testid="btn_back"]')
    page.wait_for_timeout(1000)
    expect(page.locator('[data-testid="txt_unsave"]')).to_have_text("변경사항을 저장하지 않으시겠습니까?", timeout=3000)
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_confirm"]')
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_back"]')    
    page.wait_for_timeout(1000)
    expect(page).to_have_url(URLS["cen_category"], timeout=3000)
    page.wait_for_timeout(1000)






# ✅시술 관리 


# ✅상품 관리 


# ✅상품 페이지 관리 

