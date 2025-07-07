from playwright.sync_api import Page, expect
from helpers.customer_utils import cen_login  
from helpers.product_utils import (generate_names, update_product_fields, check_save_popup, 
                                   get_product_fields, verify_dropdown_values, update_category_name
)
from config import URLS


def test_category_register(page: Page):
    # 이름 생성 
    main_ko, main_en = generate_names("대분류")
    print(main_ko)  # 대분류_0701_1
    print(main_en)  # main_0701_1
    
    mid_ko, mid_en = generate_names("중분류")
    print(mid_ko)  # 중분류_0701_1
    print(mid_en)  # mid_0701_1

    sub_ko, sub_en = generate_names("소분류")
    print(sub_ko)  # 소분류_0701_2
    print(sub_en)  # sub_0701_2

    cen_login(page) 
    page.goto(URLS["cen_category"])
    page.wait_for_timeout(3000)

    # 대분류 등록 
    page.click('[data-testid="btn_register_main"]') 
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_main_ko"]', main_ko)
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_main_en"]', main_en)
    page.wait_for_timeout(500)    
    expect(page.locator('[data-testid="toast_complete_main"]')).to_be_visible(timeout=3000)
    print("✅ 대분류 등록 완료")
    update_product_fields(new_main=main_ko)
    page.wait_for_timeout(2000)
        
    # 중분류 등록 
    page.click('[data-testid="btn_register_mid"]') 
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_mid_ko"]', mid_ko)
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_mid_en"]', mid_en)
    page.wait_for_timeout(500)    
    expect(page.locator('[data-testid="toast_complete_mid"]')).to_be_visible(timeout=3000)
    print("✅ 중분류 등록 완료")
    update_product_fields(new_mid=mid_ko)
    page.wait_for_timeout(2000)

    # 소분류 등록 
    page.click('[data-testid="btn_register_sub"]') 
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_sub_ko"]', sub_ko)
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_sub_en"]', sub_en)
    page.wait_for_timeout(500)    
    expect(page.locator('[data-testid="toast_complete_sub"]')).to_be_visible(timeout=3000)
    print("✅ 소분류 등록 완료")
    update_product_fields(new_sub=sub_ko)
    page.wait_for_timeout(2000)

    # 상품 등록 화면에서 노출 확인
    verify_dropdown_values(
        page=page,
        page_url=URLS["cen_product"] + "/register",
        field_pairs=[
            ("main", "new_main"),
            ("mid", "new_mid"),
            ("sub", "new_sub")
        ],
        testid_map={
            "trigger": "drop_{field}_trigger",
            "search": "drop_{field}_search",
            "item": "drop_{field}_item"
        }
    )
    # 상품페이지 등록 화면에서 노출 확인
    verify_dropdown_values(
        page=page,
        page_url=URLS["cen_page"] + "/register",
        field_pairs=[
            ("main", "new_main"),
            ("mid", "new_mid"),
            ("sub", "new_sub")
        ],
        testid_map={
            "trigger": "drop_{field}_trigger",
            "search": "drop_{field}_search",
            "item": "drop_{field}_item"
        }
    )


def test_category_edit(page: Page):
    # 수정할 데이터 지정
    fields = get_product_fields("main", "sub")
    current_main = fields["main"]
    current_mid = fields["mid"]
    current_sub = fields["sub"]
    edit_main = "대분류 수정테스트" if current_main == "대분류 수정" else "대분류 수정" # 수정 확인용  
    edit_mid = "중분류 수정테스트" if current_mid == "중분류 수정" else "중분류 수정" # 수정 확인용  
    edit_sub = "중분류 수정테스트" if current_sub == "소분류 수정" else "소분류 수정" # 수정 확인용  

    # 대분류 수정
    cen_login(page)
    page.goto(URLS["cen_category"])
    page.wait_for_timeout(3000)
    update_category_name(
        page,
        level="main",
        current_value=current_main,
        new_value= edit_main, 
        toastid="toast_edit_main"
    )
    page.wait_for_timeout(1000)

    verify_dropdown_values(
        page, 
        URLS["cen_product"]+"/register", 
        ("main","new_main"), 
        {"trigger": "drop_ctg_main_trigger", "search": "drop_ctg_main_search", "item": "drop_ctg_main_item"}
        )

    print("✅ 대분류 수정 완료")
    update_product_fields(main=edit_main)

    # 중분류 수정
    update_category_name(
        page,
        level="mid",
        current_value=current_mid,
        new_value= edit_mid, 
        toastid="toast_edit_mid"
    )
    page.wait_for_timeout(1000)
    print("✅ 중분류 수정 완료")
    update_product_fields(mid=edit_mid)

    # 소분류 수정
    update_category_name(
        page,
        level="sub",
        current_value=current_sub,
        new_value= edit_sub, 
        toastid="toast_edit_sub"
    )
    page.wait_for_timeout(1000)
    print("✅ 소분류 수정 완료")
    update_product_fields(sub=edit_sub)


    # 상품 등록 화면에서 노출 확인
    verify_dropdown_values(
        page=page,
        page_url=URLS["cen_product"] + "/register",
        field_pairs=[
            ("main", "new_main"),
            ("mid", "new_mid"),
            ("sub", "new_sub")
        ],
        testid_map={
            "trigger": "drop_{field}_trigger",
            "search": "drop_{field}_search",
            "item": "drop_{field}_item"
        }
    )
    # 상품페이지 등록 화면에서 노출 확인
    verify_dropdown_values(
        page=page,
        page_url=URLS["cen_page"] + "/register",
        field_pairs=[
            ("main", "new_main"),
            ("mid", "new_mid"),
            ("sub", "new_sub")
        ],
        testid_map={
            "trigger": "drop_{field}_trigger",
            "search": "drop_{field}_search",
            "item": "drop_{field}_item"
        }
    )
    