# 테스트 흐름
# 1. 등록된 고객 정보 불러와 [고객명] 기준 검색
# 2. 리스트 > 상세 > 수정모드 진입 -> 이탈 시 Alert 확인
# 3. [고객명] 다시 검색 수정 화면 바로 진입
# 4. 일부 데이터 수정 후 저장 -> 리스트에 반영 확인

import json
import random
from playwright.sync_api import Page, expect
from helpers.customer_utils import generate_random_birth, update_customer_in_json, cen_login
from config import URLS

CUSTOMER_FILE = "data/customers.json"

def load_one_customer():
    with open(CUSTOMER_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data[0] if data else None

def test_edit_customer_list_and_detail(page: Page):
    customer = load_one_customer()
    assert customer, "❌ 수정 대상 고객이 필요합니다."

    cen_login(page) #로그인 
    page.goto(URLS["cen_customer"])

    # ✅ 리스트 수정
    page.fill('[data-testid="input_search_phone"]', customer["phone"])
    page.click("body")
    row = page.locator("table tbody tr").first
    cells = row.locator("td")
    nationality = customer.get("nationality", "한국인")  # 기본값은 한국인

    new_list_values = {
        "customer_name": customer["customer_name"].replace("자동화", "수정됨"),
        "birth": generate_random_birth(),
        "gender": "여성" if customer["gender"] == "남성" else "남성",
        "phone": "01012345678" if nationality == "한국인" else "",
        "email": "edit@test.com" if nationality == "외국인" else "",
    }

    fields = ["customer_name", "birth", "gender"]
    if nationality == "한국인":
        fields.append("phone")
    elif nationality == "외국인":
        fields.append("email")

    for i, key in enumerate(fields):
        cell = cells.nth(i + 1)
        cell.click()
        if key == "gender":
            page.locator("select").select_option(label=new_list_values[key])
        else:
            input_box = page.locator("input").first
            input_box.fill("")
            page.click("body")
            expect(page.locator('[data-testid="toast_required"]')).to_be_visible()
            input_box.fill(new_list_values[key])
            page.click("body")

    # ✅ 상세 진입 → 리스트 수정된 전화번호 기준으로 검색
    page.fill('[data-testid="input_search_phone"]', new_list_values["phone"])
    page.click("body")
    page.wait_for_timeout(3000)
    row = page.locator("table tbody tr").first
    last_cell = row.locator("td").last
    last_cell.click()
    page.wait_for_timeout(2000)
    page.locator('[data-testid="btn_edit"]').first.click()
    page.wait_for_timeout(3000)

    # ✅ 상세 정보 수정
    new_detail_values = {
        "customer_name": new_list_values["customer_name"] + "(최종)",
        "birth": generate_random_birth(),
        "gender": "여성" if new_list_values["gender"] == "남성" else "남성",
        "phone": "01098765432" if nationality == "한국인" else "",
        "email": "test@medisolveai.com" if nationality == "외국인" else "",
    }

    page.fill('[data-testid="input_name"]', new_detail_values["customer_name"])
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_birth"]', new_detail_values["birth"])
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_gender"]').select_option(label=new_detail_values["gender"])
    page.wait_for_timeout(1000)

    # 국적별 입력 처리
    if nationality == "한국인":
        page.fill('[data-testid="input_phone"]', new_detail_values["phone"])
    elif nationality == "외국인":
        page.fill('[data-testid="input_email"]', new_detail_values["email"])

    page.wait_for_timeout(1000)
    page.locator('[data-testid="btn_confirm"]').click()
    page.wait_for_timeout(2000)
    page.locator('[data-testid="btn_yes"]').click()                         

    # ✅ 고객관리 리스트 수정 확인
    page.goto(URLS["cen_customer"])
    page.wait_for_timeout(3000)
    page.fill('[data-testid="input_search_phone"]', new_detail_values["phone"])
    page.wait_for_timeout(1000)
    page.click("body")
    page.wait_for_timeout(3000)
    row = page.locator("table tbody tr").first
    row_text = row.inner_text()
    assert new_detail_values["customer_name"] in row_text
    assert new_detail_values["email"] in row_text

    # ✅ 예약관리 리스트 수정 확인
    page.goto(URLS["cen_reservation"])
    page.wait_for_timeout(3000)
    page.fill('[data-testid="input_search_phone"]', new_detail_values["phone"])
    page.wait_for_timeout(1000)
    page.click("body")
    page.wait_for_timeout(3000)
    row = page.locator("table tbody tr").first
    row_text = row.inner_text()
    assert new_detail_values["customer_name"] in row_text
    assert new_detail_values["email"] in row_text
    print(f"✅예약관리에서 고객 정보 확인 완료: {new_detail_values['customer_name']}")

    # ✅ JSON 업데이트
    update_customer_in_json(customer["customer_name"], new_detail_values)
