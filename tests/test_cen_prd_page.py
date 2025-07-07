from config import URLS
import random
from playwright.sync_api import Page, expect
from helpers.customer_utils import cen_login  
from helpers import image_assets as img
from helpers.product_utils import (
    generate_names, update_product_fields, check_save_popup, get_product_fields, 
    verify_dropdown_values, generate_descriptions, generate_price_info, fill_group_price_info, upload_image,
    select_category
)
field=get_product_fields("new_main","new_mid", "new_sub", "new_product")

def test_page_register(page: Page):
    cen_login(page) 
    page.goto(URLS["cen_page"])
    page.wait_for_timeout(2000)
    page.locator('[data-testid="btn_register"]').click
    page.wait_for_timeout(1000)

    select_category(page, "main", field["new_main"])
    select_category(page, "mid", field["new_mid"])
    select_category(page, "sub", field["new_sub"])

    # 설명 입력 
    description = generate_descriptions()
    page.fill('[data-testid="input_description"]', description["des_ko"]) 
    page.wait_for_timeout(1000)
    
    # 이미지 업로드
    upload_image(page, img.edit_detail, "img_edit_detail.png")

    # 노출 상품 선택
    page.click('[data-testid="drop_display_prd_trigger"]')
    page.wait_for_timeout(1000)
    page.fill('[data-testid="drop_display_prd_search"]', field["new_product"])
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_display_prd_item"]', has_text=field["new_product"]).first.click()
    page.wait_for_timeout(1000)
    
    # 콘텐츠 명 
    page.locator('[data-testid="btn_add_group"]').click()
    content = field["new_product"] + "콘텐츠"
    page.fill('[data-testid="input_content"]', content)
    # 콘텐츠 이미지 
    upload_image(page, img.detail_img_5, "img_event_5.jpg")


    # 영어 전환 후 등록
    # ⚠️ 기획 확정 후 수정 필요 
    
    # 설명 입력 
    description = generate_descriptions()
    page.fill('[data-testid="input_description"]', description["des_en"]) 
    page.wait_for_timeout(1000)
    
    # 이미지 업로드
    upload_image(page, img.edit_detail, "img_edit_detail.png")

    # 콘텐츠 명 
    page.locator('[data-testid="btn_add_group"]').click()
    content = field["new_product"] + "Content"
    page.fill('[data-testid="input_content"]', content)

    # 콘텐츠 이미지 
    upload_image(page, img.edit_detail, "img_edit_detail.jpg")
    
    # 저장 
    page.click('[data-testid="btn_complete"]')
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_complete"]')).to_be_visible(timeout=3000)
    print("✅ 상품페이지 등록 완료")
    page.wait_for_timeout(1000)

def test_page_edit(page: Page):
    cen_login(page) 
    page.goto(URLS["cen_page"])
    page.wait_for_timeout(3000)
    page.click('[data-testid="drop_status_trigger"]')  
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_status_item"]', has_text="노출").click()    
    page.wait_for_timeout(1000)
    page.fill('[data-testid="search_name"]', field["new_sub"])
    page.locator("body").click(position={"x": 10, "y": 10})
    page.wait_for_timeout(1000)

    row = page.locator("table tbody tr").first
    row.locator("td").last.click()
    page.wait_for_timeout(2000)
    page.locator('[data-testid="btn_review"]').click()
    page.wait_for_timeout(1000)
    page.locator('[data-testid="btn_edit"]').click()
    page.wait_for_timeout(1000)

    # 상품 추가
    product = "자동화상품"
    page.locator('[data-testid="drop_display_prd_trigger"]').last.click()
    page.wait_for_timeout(1000)
    page.fill('[data-testid="drop_display_prd_search"]', product)
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_display_prd_item"]', has_text=product).first.click()
    page.wait_for_timeout(1000)

    # 콘텐츠 1 수정
    content_1 = "[수정] " + field["new_product"] + " 콘텐츠"
    page.fill('[data-testid="input_content"]', content_1)

    # 콘텐츠 2 추가 
    content_2 = field["new_product"] + " 콘텐츠"
    page.locator('[data-testid="btn_add_group"]').click()
    page.wait_for_timeout(1000)
    page.locator('[data-testid="input_content"]').nth(1).fill(content_2)
    page.wait_for_timeout(1000)
    
    # 콘텐츠 이미지 
    upload_image(page, img.detail_img_5, "img_event_5.jpg")

    # 저장 
    page.click('[data-testid="btn_complete"]')
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_edit"]')).to_be_visible(timeout=3000)
    print("✅ 상품페이지 수정 완료")
    page.wait_for_timeout(1000)