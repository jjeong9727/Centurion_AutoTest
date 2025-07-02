from config import URLS
import random
from playwright.sync_api import Page, expect
from helpers.customer_utils import cen_login  
from helpers import image_assets as img
from helpers.product_utils import (
    generate_names, update_product_fields, check_save_popup, get_product_fields, 
    verify_dropdown_values, generate_descriptions, generate_price_info, fill_group_price_info, upload_image

)

def test_product_register(page: Page):
    # 이름 생성 
    product_ko, product_en = generate_names("상품명")
    print(product_ko)  # 상품명_0701_1
    print(product_en)  # product_0701_1
    # 시술 불러오기
    fields = get_product_fields("new_treat")
    treat = fields["new_treat"]
    # 상품 가격 생성 
    price_info_1 = generate_price_info() 

    cen_login(page) 
    page.goto(URLS["cen_product"])
    page.wait_for_timeout(2000)
    page.click('[data-testid="btn_register"]')  
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_name"]', product_ko)
    page.wait_for_timeout(1000)
    # 설명 입력
    description_data = generate_descriptions()
    page.fill('[data-testid="input_description_main"]', description_data["main_ko"])
    page.fill('[data-testid="input_description_sub"]', description_data["sub_ko"])

    # 이미지 업로드
    upload_image(page, img.detail_img_5, "img_event_5.jpg")
    
    # 시술선택
    page.click('[data-testid="drop_treat_trigger"]') 
    page.wait_for_timeout(1000)
    page.fill('[data-testid="drop_treat_search"]', treat) 
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_treat_item"]', has_text=treat).first.click()
    page.wait_for_timeout(1000)
    fill_group_price_info(page, 1, price_info_1)
    
    # 영어로 전환하여 정보 입력 
    page.click('[data-testid="tab_eng"]') 
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_name"]', product_en)
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_description_main"]', description_data["main_en"])
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_description_sub"]', description_data["sub_en"])
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_complete"]')
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_complete"]')).to_be_visible(timeout=3000)
    print("✅ 상품 등록 완료")
    page.wait_for_timeout(1000)
    update_product_fields(new_product=product_ko)
    # 상품페이지 등록화면 노출 확인 
    verify_dropdown_values(
        page=page,
        page_url=URLS["cen_page"] + "/register",
        field_pairs=[("product", "new_product")],
        testid_map={
            "trigger": "drop_display_prd_trigger",
            "search": "drop_display_prd_search",
            "item": "drop_display_prd_item"
        }
    )


def test_product_edit(page: Page):
    # 수정할 데이터 지정
    fields = get_product_fields("new_product")
    current_product = fields["new_product"]
    edit_product = "[수정]"+ current_product # 수정 확인용 
    # 상세 화면 진입
    cen_login(page)
    page.goto(URLS["cen_product"])
    page.wait_for_timeout(3000)
    page.fill('[data-testid="search_name"]', current_product)
    page.locator("body").click(position={"x": 10, "y": 10})
    page.wait_for_timeout(1000)
    row = page.locator("table tbody tr").first
    row.locator("td").last.click()
    page.wait_for_timeout(2000)
    page.locator('[data-testid="btn_review"]').click()
    page.wait_for_timeout(1000)
    expect(page.locator(f'[data-testid="product_name"]')).to_have_text(current_product, timeout=3000)
    page.wait_for_timeout(500)
    # 수정 화면 진입
    page.locator('[data-testid="btn_edit"]').click()
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_category_name"]', edit_product)
    page.wait_for_timeout(1000)

    # 시술 추가
    price_info_1 = generate_price_info() # 시술 그룹1 수정용
    price_info_2 = generate_price_info() # 시술 그룹2 추가용 

    # 그룹 01 - 시술 추가 및 횟수 정가 할인가 할인율 수정
    treat="자동화시술"
    page.locator('[data-testid="btn_add_treat"]').click()
    page.locator('[data-testid="drop_treat_trigger"]').last.click()
    page.wait_for_timeout(1000)
    page.fill('[data-testid="drop_treat_search"]', treat) 
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_treat_item"]', has_text=treat).first.click()
    page.wait_for_timeout(1000) 
    
    fill_group_price_info(page, 1, price_info_1) 
    
    # 그룹02 - 시술 1
    page.click('[data-testid="btn_add_group"]') # 그룹2 생성
    page.locator('[data-testid="drop_treat_trigger"]').last.click()
    page.wait_for_timeout(1000)
    page.fill('[data-testid="drop_treat_search"]', treat) 
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_treat_item"]', has_text=treat).first.click()
    page.wait_for_timeout(1000) 

    fill_group_price_info(page, 2, price_info_2)

    page.click('[data-testid="btn_complete"]')
    page.wait_for_timeout(1000)
    check_save_popup(
        page,
        popup_textid = "txt_edit",
        confirm_text = "상품을 수정하시겠습니까?",
        toast_testid = "toast_edit"
    )
    print("✅ 상품 정보 수정 완료")
    update_product_fields(new_product=edit_product)


    