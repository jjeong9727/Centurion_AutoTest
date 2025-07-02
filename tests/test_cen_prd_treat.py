from playwright.sync_api import Page, expect
from helpers.customer_utils import cen_login  
from helpers.product_utils import generate_names, update_product_fields, check_save_popup, get_product_fields, verify_dropdown_values
from config import URLS


def test_treatment_register(page: Page):
    # 이름 생성 
    treat_ko, treat_en = generate_names("시술명")
    print(treat_ko)  # 시술명_0701_1

    cen_login(page) 
    page.goto(URLS["cen_treat"])
    page.wait_for_timeout(3000)
    page.click('[data-testid="btn_register"]') 
    page.wait_for_timeout(1000)

    page.fill('[data-testid="input_name"]', treat_ko)
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_confirm"]')
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_complete"]')).to_be_visible(timeout=3000)
    
    print("✅ 시술 등록 완료")
    update_product_fields(new_treat=treat_ko)
    # 상품 등록 화면 노출 확인 
    verify_dropdown_values(
        page=page,
        page_url=URLS["cen_product"] + "/register",
        field_pairs=[("treat", "new_treat")],
        testid_map={
            "trigger": "drop_treat_trigger",
            "search": "drop_treat_search",
            "item": "drop_treat_item"
        }
    )
    page.wait_for_timeout(1000)

def test_treatment_edit(page: Page):
    # 수정할 데이터 지정
    fields = get_product_fields("treat")
    current_treat = fields["treat"]
    edit_treat = "시술명수정테스트" if current_treat == "시술명수정" else "시술명수정" # 수정 확인용  

    # 시술명 수정
    cen_login(page)
    page.goto(URLS["cen_treat"])
    page.wait_for_timeout(3000)
    page.fill('[data-testid="search_name"]', current_treat)
    page.wait_for_timeout(1000)
    row = page.locator("table tbody tr").first
    cell = row.locator("td")
    cell.click()
    page.wait_for_timeout(1000)
    input_box = cell.locator("input").first
    input_box.fill(edit_treat)
    page.wait_for_timeout(500)
    page.locator("body").click(position={"x": 10, "y": 10})
    page.wait_for_timeout(500)
    check_save_popup(
        page,
        popup_textid = "txt_edit",
        confirm_text = "시술명을 수정하시겠습니까?",
        toast_testid = "toast_complete"
    )
    print("✅ 시술 수정 확인 완료")
    update_product_fields(treat = edit_treat)



    