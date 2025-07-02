import pytest
import json
import re
from playwright.sync_api import Page, expect
from helpers.customer_utils import cen_login  
from helpers.product_utils import (check_unsave_popup, switch_to_hidden, switch_to_visible, 
                                    check_save_popup, delete_all_items, check_invalid_upload,
                                    search_and_verify
)
from config import URLS
from helpers import image_assets as img

# ✅테스트 데이터 지정===================================================================================
EDIT_JSON_PATH = "data/product.json"
with open(EDIT_JSON_PATH, "r", encoding="utf-8") as f:
    edit_data = json.load(f)
 
current_main = edit_data["main"]
ctg_main = "자동화대분류" # 중복 확인용 

current_sub = edit_data["sub"]
ctg_sub = "자동화중분류" # 중복 확인용 

current_treat = edit_data["treat"]
treat = "자동화시술" # 중복 확인용 

current_product = edit_data["product"]
product = "자동화상품"

current_title = edit_data["title"]
title = "자동화상품페이지"

# ✅상품 분류=====================================================================================================

# 상품 분류 관리 중복 확인
def test_category_duplicate(page: Page):
    cen_login(page) 
    page.goto(URLS["cen_category"])
    page.wait_for_timeout(3000)
    # 검색 기능 확인 
    search_and_verify(
        page=page,
        type_trigger_id="drop_type_trigger",
        type_item_id="drop_type_item",
        type_text="대분류",
        type_column_index=0,
        search_field_id="search_name",
        search_value=ctg_main,
        table_selector="table tbody tr"
    )
    # 등록 진입     
    page.click('[data-testid="btn_register"]') 
    page.wait_for_timeout(1000)

    # 대분류 등록 화면 중복 토스트 확인 (한국어 중복)
    page.click('[data-testid="drop_type_trigger"]')  
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_type_item"]', has_text="대분류").click()    
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_category_name"]', ctg_main)
    page.wait_for_timeout(1000)
    page.click('[data-testid="tab_eng"]')
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_category_name"]', ctg_sub)
    page.wait_for_timeout(1000)    
    page.click('[data-testid="btn_complete"]')
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_duplicate_main"]')).to_be_visible(timeout=3000)
    print("✅ 대분류 중복 토스트 확인 완료")
    page.wait_for_timeout(1000)

    # 중분류 등록 화면 중복 토스트 확인 (영어 중복)
    page.click('[data-testid="drop_type_trigger"]')  
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_type_item"]', has_text="중분류").click()    
    page.wait_for_timeout(1000)
    
    page.fill('[data-testid="input_category_name"]', ctg_main)
    page.wait_for_timeout(1000)
    page.click('[data-testid="tab_eng"]')
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
    page.wait_for_timeout(1000)

    row = page.locator("table tbody tr").first
    row.locator("td").last.click()
    page.wait_for_timeout(2000)
    page.locator('[data-testid="btn_review"]').click()
    page.wait_for_timeout(1000)

    page.locator('[data-testid="btn_edit"]').click()
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_category_name"]', ctg_main)
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_complete"]')
    page.wait_for_timeout(1000)
    check_save_popup(
        page,
        popup_textid = "txt_edit",
        confirm_text = "상품 분류명을 수정하시겠습니까?",
        toast_testid = "toast_duplicate_main"
    )
    print("✅ 대분류 중복 토스트 확인 완료")

    # 수정 화면 이탈 팝업 확인 후 상세로 이동 확인 
    check_unsave_popup(page)
    expect(page).to_have_url(re.compile(f"^{re.escape(URLS['cen_category'])}"), timeout=3000)
    page.wait_for_timeout(1000)    

# 상품 분류 관리 노출 미노출 전환 (비활성화 상태에서 시작)
def test_category_toggle(page: Page):    
    # 리스트에서 미노출 / 노출 변경 팝업 및 토스트 확인
    cen_login(page) 
    page.goto(URLS["cen_category"])
    page.wait_for_timeout(3000)

    page.fill('[data-testid="search_name"]', current_main)
    page.locator("body").click(position={"x": 10, "y": 10})
    page.wait_for_timeout(1000)

    switch_to_visible(
        page,
        toggle_testid="toggle_status",
        popup_textid="txt_change_visible",
        confirm_text="상품 분류를 노출 상태로 변경하시겠습니까?",
        toast_testid="toast_status"
    )   
    switch_to_hidden(
        page,
        toggle_testid="toggle_status",
        popup_textid="txt_change_hidden",
        confirm_text="상품 분류를 미노출 상태로 변경하시겠습니까?",
        toast_testid="toast_status"
    )

# ✅시술관리 =====================================================================================================
# 시술 관리 중복 확인 
def test_treat_duplicate(page: Page):
    cen_login(page) 
    page.goto(URLS["cen_treat"])
    page.wait_for_timeout(3000)
    # 검색 기능 확인 
    search_and_verify(
        page=page,
        search_field_id="search_name",
        search_value=treat,
        table_selector="table tbody tr"
    )

    # 등록 팝업 중복 토스트 확인 
    page.click('[data-testid="btn_register"]')  
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_name"]', treat)
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_cancel"]')
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_register"]')  
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_name"]', treat)
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_complete"]')
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_duplicate_treat"]')).to_be_visible(timeout=3000)
    print("✅ 시술명 중복 토스트 확인 완료")
    page.click('[data-testid="btn_cancel"]')
    page.wait_for_timeout(1000)

    # 리스트 화면 중복 토스트 확인
    page.fill('[data-testid="search_name"]', current_treat)
    page.wait_for_timeout(1000)
    row = page.locator("table tbody tr").first
    cell = row.locator("td")
    cell.click()
    page.wait_for_timeout(1000)
    input_box = cell.locator("input").first
    input_box.fill("")
    page.wait_for_timeout(500)
    page.locator("body").click(position={"x": 10, "y": 10})
    page.wait_for_timeout(500)
    check_save_popup(
        page,
        popup_textid = "txt_edit",
        confirm_text = "시술명을 수정하시겠습니까?",
        toast_testid = "toast_required"
    )
    print("✅ 상품 중복 토스트 확인 완료")
    input_box.fill(treat)
    page.wait_for_timeout(500)
    page.locator("body").click(position={"x": 10, "y": 10})
    page.wait_for_timeout(500)
    check_save_popup(
        page,
        popup_textid = "txt_edit",
        confirm_text = "시술명을 수정하시겠습니까?",
        toast_testid = "toast_duplicate_treat"
    )
    page.wait_for_timeout(1000)

# 시술 관리 활성 비활성 전환 (비활성 상태에서 시작)
def test_treat_toggle(page: Page):
    cen_login(page) 
    page.goto(URLS["cen_treat"])
    page.wait_for_timeout(3000)

    page.fill('[data-testid="search_name"]', current_treat)
    page.locator("body").click(position={"x": 10, "y": 10})
    page.wait_for_timeout(1000)
    row = page.locator("table tbody tr").first
    row.locator(f'[data-testid="toggle_use"]').click()

    switch_to_hidden(
        page,
        toggle_testid="toggle_use",
        popup_textid="txt_disable",
        confirm_text="시술을 비활성화 하시겠습니까?",
        toast_testid="toast_disable"
    )

    # 미노출 불가 토스트 확인 (상품에 등록 및 활성 상태)
    page.reload()
    page.wait_for_timeout(2000)

    page.fill('[data-testid="search_name"]', treat)
    page.locator("body").click(position={"x": 10, "y": 10})
    page.wait_for_timeout(1000)
    row = page.locator("table tbody tr").first
    row.locator(f'[data-testid="toggle_use"]').click()
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_using"]')).to_be_visible(timeout=3000)

# ✅상품 관리 =====================================================================================================
# 상품 관리 중복 확인 
def test_product_duplicate(page:Page):
    cen_login(page) 
    page.goto(URLS["cen_product"])
    page.wait_for_timeout(3000)
    # 검색 기능 확인 
    search_and_verify(
        search_field_id="search_name",
        search_value=product,
        table_selector="table tbody tr"
    )

    # 등록화면 중복 확인(영어 중복)
    page.click('[data-testid="btn_register"]')  
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_name"]', current_treat)
    page.wait_for_timeout(1000)
    page.click('[data-testid="drop_treat_trigger"]') 
    page.wait_for_timeout(1000)
    page.fill('[data-testid="drop_treat_search"]', treat) 
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_treat_item"]', has_text=treat).first.click()
    page.wait_for_timeout(1000)
    page.click('[data-testid="tab_eng"]') 
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_name"]', product)
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_complete"]')
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_duplicate_main"]')).to_be_visible(timeout=3000)
    print("✅ 상품명 중복 토스트 확인 완료")
    page.wait_for_timeout(1000)
    
    # 시술 개수 제한 확인 
    for _ in range(10):
        page.click('[data-testid="btn_add_treat"]')
        page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_overstack"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    # 시술 삭제 확인 
    delete_all_items(page, "btn_delete_treat")

    # 시술그룹 개수 제한 확인 
    for _ in range(10):
        page.click('[data-testid="btn_add_group"]')
        page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_overstack"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    # 시술 그룹 삭제 확인
    delete_all_items(page, "btn_delete_group")
    # 이미지 업로드 유효성 확인 
    check_invalid_upload(page, img.overspec_img, "toast_image_size")
    page.wait_for_timeout(1000)
    check_invalid_upload(page, img.nonspec_img, "toast_image_format")
    page.wait_for_timeout(1000)
    check_invalid_upload(page, img.nonspec_video, "toast_image_format")
    page.wait_for_timeout(1000)

    # 등록화면 이탈 팝업 확인 
    check_unsave_popup(page)
    expect(page).to_have_url(URLS["cen_product"], timeout=3000)
    page.wait_for_timeout(1000) 

    # 수정 화면에서 중복 확인 (한국어 중복)
    page.fill('[data-testid="search_name"]', current_product)
    page.locator("body").click(position={"x": 10, "y": 10})
    page.wait_for_timeout(1000)

    row = page.locator("table tbody tr").first
    row.locator("td").last.click()
    page.wait_for_timeout(2000)
    page.locator('[data-testid="btn_review"]').click()
    page.wait_for_timeout(1000)

    page.locator('[data-testid="btn_edit"]').click()
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_name"]', product)
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_complete"]')
    page.wait_for_timeout(1000)
    check_save_popup(
        page,
        popup_textid = "txt_edit",
        confirm_text = "상품을 수정하시겠습니까?",
        toast_testid = "toast_duplicate_prd"
    )
    print("✅ 상품 중복 토스트 확인 완료")

    # 수정 화면 이탈 팝업 확인 후 상세로 이동 확인 
    check_unsave_popup(page)
    expect(page).to_have_url(re.compile(f"^{re.escape(URLS['cen_product'])}"), timeout=3000)
    page.wait_for_timeout(1000)    
  
# 상품 관리 활성 비활성 전환 (비활성 상태에서 시작)
def test_product_toggle(page:Page):
    cen_login(page) 
    page.goto(URLS["cen_product"])
    page.wait_for_timeout(3000)

    page.fill('[data-testid="search_name"]', current_product)
    page.locator("body").click(position={"x": 10, "y": 10})
    page.wait_for_timeout(1000)
    row = page.locator("table tbody tr").first
    row.locator(f'[data-testid="toggle_use"]').click()
    page.wait_for_timeout(1000)

    switch_to_hidden(
        page,
        toggle_testid="toggle_use",
        popup_textid="txt_disable",
        confirm_text="상품을 비활성화 하시겠습니까?",
        toast_testid="toast_disable"
    )

    # 미노출 불가 토스트 확인 (상품 페이지에 등록 및 활성 상태)
    page.reload()
    page.wait_for_timeout(2000)

    page.fill('[data-testid="search_name"]', product)
    page.locator("body").click(position={"x": 10, "y": 10})
    page.wait_for_timeout(1000)
    row = page.locator("table tbody tr").first
    row.locator(f'[data-testid="toggle_use"]').click()
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_using"]')).to_be_visible(timeout=3000)

# ✅상품 페이지 관리=====================================================================================================
# 상품 페이지 관리 중복 확인 
def test_page_duplicate(page:Page):
    cen_login(page) 
    page.goto(URLS["cen_page"])
    page.wait_for_timeout(3000)
    # 검색 기능 확인 
    search_and_verify(
        page=page,
        type_trigger_id="drop_status_trigger",
        type_item_id="drop_status_item",
        type_text="노출",
        type_column_index=4,
        search_field_id="search_name",
        search_value=title,
        table_selector="table tbody tr",
        visible=True
    )

    # 등록화면 중복 확인(영어 중복)
    page.click('[data-testid="btn_register"]')  
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_title"]', product)
    page.wait_for_timeout(1000)
    page.click('[data-testid="drop_display_prd_trigger"]')
    page.wait_for_timeout(1000)
    page.fill('[data-testid="drop_display_prd_search"]', product)
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_display_prd_item"]', has_text=product).first.click()
    page.wait_for_timeout(1000)
    page.click('[data-testid="tab_eng"]')
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_title"]', title)
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_complete"]')
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_duplicate_title"]')).to_be_visible(timeout=3000)
    print("✅ 상품페이지 타이틀 중복 토스트 확인 완료")
    page.wait_for_timeout(1000)

    # 노출 상품 개수 제한 없음 확인 
    for _ in range(15):
        page.click('[data-testid="btn_add_prd"]')
        page.wait_for_timeout(1000)
    # 노출 상품 삭제 확인
    delete_all_items(page, "btn_delete_prd")

    # 컨텐츠 개수 제한 없음 확인 
    for _ in range(15):
        page.click('[data-testid="btn_add_group"]')
        page.wait_for_timeout(1000)
    # 컨텐츠 삭제 확인
    delete_all_items(page, "btn_delete_group")

    # 이미지 업로드 유효성 확인 
    check_invalid_upload(page, img.overspec_img, "toast_image_size")
    page.wait_for_timeout(1000)
    check_invalid_upload(page, img.nonspec_img, "toast_image_format")
    page.wait_for_timeout(1000)
    check_invalid_upload(page, img.nonspec_video, "toast_image_format")
    page.wait_for_timeout(1000)
    
    # 등록화면 이탈 팝업 확인 
    check_unsave_popup(page)
    expect(page).to_have_url(URLS["cen_page"], timeout=3000)
    page.wait_for_timeout(1000) 

    # 수정 화면 중복 확인(한국어 중복)
    page.fill('[data-testid="search_name"]', current_title)
    page.locator("body").click(position={"x": 10, "y": 10})
    page.wait_for_timeout(1000)

    row = page.locator("table tbody tr").first
    row.locator("td").last.click()
    page.wait_for_timeout(2000)
    page.locator('[data-testid="btn_review"]').click()
    page.wait_for_timeout(1000)

    page.locator('[data-testid="btn_edit"]').click()
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_name"]', title)
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_complete"]')
    page.wait_for_timeout(1000)
    expect(page.locator('[data-testid="toast_duplicate_title"]')).to_be_visible(timeout=3000)
    print("✅ 상품 중복 토스트 확인 완료")

    # 수정 화면 이탈 팝업 확인 후 상세로 이동 확인 
    check_unsave_popup(page)
    expect(page).to_have_url(re.compile(f"^{re.escape(URLS['cen_page'])}"), timeout=3000)
    page.wait_for_timeout(1000)   

# 상품 페이지 활성 비활성 전환 (비활성 상태에서 시작)
def test_page_toggle(page: Page):
    cen_login(page) 
    page.goto(URLS["cen_page"])
    page.wait_for_timeout(3000)

    page.fill('[data-testid="search_name"]', current_title)
    page.locator("body").click(position={"x": 10, "y": 10})
    page.wait_for_timeout(1000)

    switch_to_visible(
        page,
        toggle_testid="toggle_status",
        popup_textid="txt_change_visible",
        confirm_text="상품 페이지를 노출 상태로 변경하시겠습니까?",
        toast_testid="toast_status"
    )   
    switch_to_hidden(
        page,
        toggle_testid="toggle_status",
        popup_textid="txt_change_hidden",
        confirm_text="상품 페이지를 미노출 상태로 변경하시겠습니까?",
        toast_testid="toast_status"
    )