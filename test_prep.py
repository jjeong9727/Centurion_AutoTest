import pytest
import json
import re
from playwright.sync_api import Page, expect
from helpers.customer_utils import cen_login  
from helpers.product_utils import select_category
from config import URLS
from helpers import image_assets as img

main_ko = "자동화 대분류"
main_en = "auto main"
mid_ko = "자동화 중분류"
mid_en = "auto mid"
sub_ko = "자동화 소분류"
sub_en = "auto sub"
edit_main_ko = "대분류 수정테스트"
edit_main_en = "edit main"
edit_mid_ko = "중분류 수정테스트"
edit_mid_en = "edit mid"
edit_sub_ko = "소분류 수정테스트"
edit_sub_en = "edit sub"

treat_ko = "자동화 시술"
edit_treat_ko = "시술명 수정테스트"

product_ko = "자동화 상품"
product_en = "auto product"
edit_product_ko = "상품명 수정테스트"
edit_product_en = "edit product"


# 상품 분류 
def test_prep_category (page:Page):
    cen_login(page)
    page.goto(URLS["cen_category"])
    page.wait_for_timeout(3000)
    # 대분류 "자동화 대분류"
    page.click('[data-testid="btn_register_main"]') 
    page.wait_for_timeout(1000)    
    page.fill('[data-testid="input_main_ko"]', main_ko)
    page.wait_for_timeout(500)
    page.fill('[data-testid="input_main_en"]', main_en)
    page.wait_for_timeout(500)
    page.locator('[data-testid="btn_confirm"]').click()
    page.wait_for_timeout(1000)    
    # 대분류 "대분류 수정테스트"
    page.click('[data-testid="btn_register_main"]') 
    page.wait_for_timeout(1000)    
    page.fill('[data-testid="input_main_ko"]', edit_main_ko)
    page.wait_for_timeout(500)
    page.fill('[data-testid="input_main_en"]', edit_main_en)
    page.wait_for_timeout(500)
    page.locator('[data-testid="btn_confirm"]').click()
    page.wait_for_timeout(1000)    

    # 중분류 "자동화 중분류"
    page.click('[data-testid="btn_register_mid"]') 
    page.wait_for_timeout(1000)    
    page.fill('[data-testid="input_mid_ko"]', mid_ko)
    page.wait_for_timeout(500)
    page.fill('[data-testid="input_mid_en"]', mid_en)
    page.wait_for_timeout(500)
    page.locator('[data-testid="btn_confirm"]').click()
    page.wait_for_timeout(1000)    
    # 대분류 "중분류 수정테스트"
    page.click('[data-testid="btn_register_mid"]') 
    page.wait_for_timeout(1000)    
    page.fill('[data-testid="input_mid_ko"]', edit_mid_ko)
    page.wait_for_timeout(500)
    page.fill('[data-testid="input_mid_en"]', edit_mid_en)
    page.wait_for_timeout(500)
    page.locator('[data-testid="btn_confirm"]').click()
    page.wait_for_timeout(1000)    

    # 소분류 "자동화 소분류"
    page.click('[data-testid="btn_register_sub"]') 
    page.wait_for_timeout(1000)    
    page.fill('[data-testid="input_sub_ko"]', sub_ko)
    page.wait_for_timeout(500)
    page.fill('[data-testid="input_sub_en"]', sub_en)
    page.wait_for_timeout(500)
    page.locator('[data-testid="btn_confirm"]').click()
    page.wait_for_timeout(1000)    
    # 소분류 "소분류 수정테스트"
    page.click('[data-testid="btn_register_sub"]') 
    page.wait_for_timeout(1000)    
    page.fill('[data-testid="input_sub_ko"]', edit_sub_ko)
    page.wait_for_timeout(500)
    page.fill('[data-testid="input_sub_en"]', edit_sub_en)
    page.wait_for_timeout(500)
    page.locator('[data-testid="btn_confirm"]').click()
    page.wait_for_timeout(1000)    

# 시술 관리
def test_prep_treat (page:Page):
    cen_login(page) 
    page.goto(URLS["cen_treat"])
    page.wait_for_timeout(3000)
    # 자동화 시술
    page.click('[data-testid="btn_register"]') 
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_name"]', treat_ko)
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_confirm"]')
    page.wait_for_timeout(1000)
    # 시술명 수정테스트
    page.click('[data-testid="btn_register"]') 
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_name"]', edit_treat_ko)
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_confirm"]')
    page.wait_for_timeout(1000)
# 상품 관리 
def test_prep_product(page:Page):
    cen_login(page) 
    page.goto(URLS["cen_product"])
    page.wait_for_timeout(2000)
    # 자동화 상품
    page.click('[data-testid="btn_register"]')  
    page.wait_for_timeout(1000)
    select_category(page, "main", main_ko)
    select_category(page, "mid", mid_ko)
    select_category(page, "sub", sub_ko)
    page.fill('[data-testid="input_name"]', product_ko)
    page.wait_for_timeout(1000)
    page.click('[data-testid="drop_treat_trigger"]') 
    page.wait_for_timeout(1000)
    page.fill('[data-testid="drop_treat_search"]', treat_ko) 
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_treat_item"]', has_text=treat_ko).first.click()
    page.wait_for_timeout(1000)
    page.locator('[data-testid="tab_en"]').click()
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_name"]', product_en)
    page.wait_for_timeout(1000)
    page.locator('[data-testid="btn_complete"]').click()
    page.wait_for_timeout(1000)
    # "상품명 수정테스트"
    page.click('[data-testid="btn_register"]')  
    page.wait_for_timeout(1000)
    select_category(page, "main", main_ko)
    select_category(page, "mid", mid_ko)
    select_category(page, "sub", sub_ko)
    page.locator('[data-testid="btn_hide"]').click()
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_name"]', edit_product_ko)
    page.wait_for_timeout(1000)
    page.click('[data-testid="drop_treat_trigger"]') 
    page.wait_for_timeout(1000)
    page.fill('[data-testid="drop_treat_search"]', treat_ko) 
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_treat_item"]', has_text=treat_ko).first.click()
    page.wait_for_timeout(1000)
    page.locator('[data-testid="tab_en"]').click()
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_name"]', edit_product_en)
    page.wait_for_timeout(1000)
    page.locator('[data-testid="btn_complete"]').click()
    page.wait_for_timeout(1000)


# 상품 페이지 관리 
def test_prep_page(page:Page):
    cen_login(page) 
    page.goto(URLS["cen_page"])
    page.wait_for_timeout(2000)

    page.locator('[data-testid="btn_register"]').click
    page.wait_for_timeout(1000)
    
    select_category(page, "main", main_ko)
    select_category(page, "mid", mid_ko)
    select_category(page, "sub", sub_ko)

    page.locator('[data-testid="btn_hide"]').click()
    page.wait_for_timeout(1000)

    page.click('[data-testid="drop_display_prd_trigger"]')
    page.wait_for_timeout(1000)
    page.fill('[data-testid="drop_display_prd_search"]', product_ko)
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_display_prd_item"]', has_text=product_ko).first.click()
    page.wait_for_timeout(1000)

    page.locator('[data-testid="btn_complete"]').click()
    page.wait_for_timeout(1000)
