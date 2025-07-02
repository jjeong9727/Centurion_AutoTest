from playwright.sync_api import Page, expect
from helpers.customer_utils import cen_login  
from helpers.product_utils import generate_names, update_product_fields, check_save_popup, get_product_fields, verify_dropdown_values
from config import URLS


def test_category_register(page: Page):
    # 이름 생성 
    main_ko, main_en = generate_names("대분류")
    print(main_ko)  # 대분류_0701_1
    print(main_en)  # main_0701_1

    sub_ko, sub_en = generate_names("중분류")
    print(sub_ko)  # 중분류_0701_2
    print(sub_en)  # sub_0701_2

    cen_login(page) 
    page.goto(URLS["cen_category"])
    page.wait_for_timeout(3000)
    page.click('[data-testid="btn_register"]') 
    page.wait_for_timeout(1000)

    # 대분류 등록 
    page.click('[data-testid="drop_type_trigger"]')  
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_type_item"]', has_text="대분류").click()    
    page.wait_for_timeout(1000)

    page.fill('[data-testid="input_category_name"]', main_ko)
    page.wait_for_timeout(1000)
    page.click('[data-testid="tab_eng"]')
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_category_name"]', main_en)
    page.wait_for_timeout(1000)    
    page.click('[data-testid="btn_complete"]')
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_complete"]')).to_be_visible(timeout=3000)
    
    print("✅ 대분류 등록 완료")
    update_product_fields(new_main=main_ko)
    # 상품페이지 등록화면  노출 확인 
    verify_dropdown_values(
        page=page,
        page_url=URLS["cen_page"] + "/register",
        field_pairs=[("main", "new_main")],
        testid_map={
            "trigger": "drop_ctg_main_trigger",
            "search": "drop_ctg_main_search",
            "item": "drop_ctg_main_item"
        }
    )
    page.wait_for_timeout(2000)
    
    # 중분류 등록 
    page.click('[data-testid="btn_register"]') 
    page.wait_for_timeout(1000)

    page.click('[data-testid="drop_type_trigger"]')  
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_type_item"]', has_text="중분류").click()    
    page.wait_for_timeout(1000)

    page.fill('[data-testid="input_category_name"]', sub_ko)
    page.wait_for_timeout(1000)
    page.click('[data-testid="tab_eng"]')
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_category_name"]', sub_en)
    page.wait_for_timeout(1000)    
    page.click('[data-testid="btn_complete"]')
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_complete"]')).to_be_visible(timeout=3000)
    print("✅ 중분류 등록 완료")
    update_product_fields(new_sub=sub_ko)
    # 상품페이지 등록화면 노출 확인 
    verify_dropdown_values(
        page=page,
        page_url=URLS["cen_page"] + "/register",
        field_pairs=[("sub", "new_sub")],
        testid_map={
            "trigger": "drop_ctg_sub_trigger",
            "search": "drop_ctg_sub_search",
            "item": "drop_ctg_sub_item"
        }
    )


def test_category_edit(page: Page):
    # 수정할 데이터 지정
    fields = get_product_fields("main", "sub")
    current_main = fields["main"]
    current_sub = fields["sub"]
    edit_main = "대분류수정테스트" if current_main == "대분류수정" else "대분류수정" # 수정 확인용  
    edit_sub = "중분류수정테스트" if current_sub == "중분류수정" else "중분류수정" # 수정 확인용  

    # 대분류 수정
    cen_login(page)
    page.goto(URLS["cen_category"])
    page.wait_for_timeout(3000)
    page.click('[data-testid="drop_type_trigger"]')  
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_type_item"]', has_text="대분류").click()    
    page.wait_for_timeout(1000)
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
    page.fill('[data-testid="input_category_name"]', edit_main)
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_complete"]')
    page.wait_for_timeout(1000)
    check_save_popup(
        page,
        popup_textid = "txt_edit",
        confirm_text = "상품 분류명을 수정하시겠습니까?",
        toast_testid = "toast_complete"
    )
    print("✅ 대분류 수정 완료")
    update_product_fields(main=edit_main)

    # 중분류 수정
    page.goto(URLS["cen_category"])
    page.wait_for_timeout(3000)
    page.click('[data-testid="drop_type_trigger"]')  
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_type_item"]', has_text="중분류").click()    
    page.wait_for_timeout(1000)
    page.fill('[data-testid="search_name"]', current_sub)
    page.locator("body").click(position={"x": 10, "y": 10})
    page.wait_for_timeout(1000)

    row = page.locator("table tbody tr").first
    row.locator("td").last.click()
    page.wait_for_timeout(2000)
    page.locator('[data-testid="btn_review"]').click()
    page.wait_for_timeout(1000)

    page.locator('[data-testid="btn_edit"]').click()
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_category_name"]', edit_sub)
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_complete"]')
    page.wait_for_timeout(1000)
    check_save_popup(
        page,
        popup_textid = "txt_edit",
        confirm_text = "상품 분류명을 수정하시겠습니까?",
        toast_testid = "toast_complete"
    )
    print("✅ 중분류 수정 완료")
    update_product_fields(sub=edit_sub)

    