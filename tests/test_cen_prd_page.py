from config import URLS
import random
from playwright.sync_api import Page, expect
from helpers.customer_utils import cen_login  
from helpers import image_assets as img
from helpers.product_utils import (
    generate_names, update_product_fields, check_save_popup, get_product_fields, 
    verify_dropdown_values, generate_descriptions, generate_price_info, fill_group_price_info, upload_image
)
def test_page_register(page: Page):
    field=get_product_fields("main", "new_main", "sub", "new_sub", "new_product")
    cen_login(page) 
    page.goto(URLS["cen_page"])
    page.wait_for_timeout(2000)
    page.locator('[data-testid="btn_register"]').click
    page.wait_for_timeout(1000)

    # 대분류 선택
    page.click('[data-testid="drop_ctg_main_trigger"]') 
    page.wait_for_timeout(1000)
    page.fill('[data-testid="drop_ctg_main_search"]', field["new_main"]) 
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_ctg_main_item"]', has_text=field["new_main"]).first.click()
    page.wait_for_timeout(1000)

    # 중분류 선택
    page.click('[data-testid="drop_ctg_sub_trigger"]') 
    page.wait_for_timeout(1000)
    page.fill('[data-testid="drop_ctg_sub_search"]', field["new_sub"]) 
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_ctg_sub_item"]', has_text=field["new_sub"]).first.click()
    page.wait_for_timeout(1000)    

    # 타이틀 입력
    title_ko= field["new_product"]+ " 상품 페이지"
    page.fill('[data-testid="input_title"]', title_ko) 
    page.wait_for_timeout(1000)

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
    content = title_ko + "콘텐츠"
    page.fill('[data-testid="input_content"]', content)

    # 콘텐츠 이미지 
    upload_image(page, img.detail_img_5, "img_event_5.jpg")


    # 영어 전환 후 등록
    # 타이틀 입력
    title_en = field["new_product"]+ " Product Page"
    page.fill('[data-testid="input_title"]', title_en) 
    page.wait_for_timeout(1000)

    # 설명 입력 
    description = generate_descriptions()
    page.fill('[data-testid="input_description"]', description["des_en"]) 
    page.wait_for_timeout(1000)
    
    # 이미지 업로드
    upload_image(page, img.edit_detail, "img_edit_detail.png")

    # 콘텐츠 명 
    content = title_en + "Content"
    page.fill('[data-testid="input_content"]', content)

    # 콘텐츠 이미지 
    upload_locator = page.locator('[data-testid="upload_content"]')
    upload_locator.wait_for(state="attached", timeout=5000)
    element = upload_locator.element_handle()
    assert element is not None, "❌ 파일 업로드 input 요소를 찾을 수 없습니다."
    element.set_input_files(img.edit_detail)
    page.wait_for_timeout(5000)
    expect(page.locator('[data-testid="txt_image"]')).to_have_text("img_edit_detail.png")
    page.wait_for_timeout(1000)
    
    # 저장 
    page.click('[data-testid="btn_complete"]')
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_complete"]')).to_be_visible(timeout=3000)
    print("✅ 상품페이지 등록 완료")
    page.wait_for_timeout(1000)
    update_product_fields(new_title = title_ko)

def test_page_edit(page: Page):
    field=get_product_fields("new_title")
    current_title = field["new_title"]
    edit_title = "[수정]"+ current_title # 수정 확인용 
    cen_login(page) 
    page.goto(URLS["cen_page"])
    page.wait_for_timeout(3000)
    page.click('[data-testid="drop_status_trigger"]')  
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_status_item"]', has_text="노출").click()    
    page.wait_for_timeout(1000)
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

    # 타이틀 수정
    page.fill('[data-testid="input_title"]', edit_title)
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
    content_1 = "[수정] " + current_title + " 콘텐츠"
    page.fill('[data-testid="input_content"]', content_1)

    # 콘텐츠 2 추가 
    content_2 = current_title + " 콘텐츠"
    page.locator('[data-testid="btn_add_group"]').click()
    page.wait_for_timeout(1000)
    page.locator('[data-testid="input_content"]').nth(1).fill(content_2)
    page.wait_for_timeout(1000)
    
    content = current_title + " 콘텐츠"
    page.fill('[data-testid="input_content"]', content)
    page.wait_for_timeout(1000)

    # 콘텐츠 이미지 
    upload_locator = page.locator('[data-testid="upload_content"]').last
    upload_locator.wait_for(state="attached", timeout=5000)
    element = upload_locator.element_handle()
    assert element is not None, "❌ 파일 업로드 input 요소를 찾을 수 없습니다."
    element.set_input_files(img.edit_detail)
    page.wait_for_timeout(5000)
    expect(page.locator('[data-testid="txt_image"]')).to_have_text("img_edit_detail.png")
    page.wait_for_timeout(1000)

    # 저장 
    page.click('[data-testid="btn_complete"]')
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_edit"]')).to_be_visible(timeout=3000)
    print("✅ 상품페이지 수정 완료")
    page.wait_for_timeout(1000)
    update_product_fields(new_title = edit_title)