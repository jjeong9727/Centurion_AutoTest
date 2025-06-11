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

def test_edit_customer_list_and_detail_single(page: Page):
    customer = load_one_customer()
    assert customer, "❌ 수정 대상 고객이 필요합니다."

    cen_login(page) #로그인 
    page.goto(URLS["cen_customer"])

    # ✅ 리스트 수정
    page.fill('[data-testid="input_search_phone"]', customer["phone"])
    page.click("body")
    row = page.locator("table tbody tr").first
    cells = row.locator("td")

    new_list_values = {
        "customer_name": customer["customer_name"].replace("자동화", "수정됨"),
        "birth": generate_random_birth(),
        "gender": "여성" if customer["gender"] == "남성" else "남성",
        "phone": "01012345678",
        "email": "edit@test.com",
    }

    fields = ["customer_name", "birth", "gender", "phone"]

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
    row.locator("td").nth(6).click()

    page.wait_for_timeout(2000)
    page.locator('[data-testid="btn_edit"]').click()
    page.wait_for_timeout(2000)

    # ✅ 상세 정보 수정
    new_detail_values = {
        "customer_name": new_list_values["customer_name"] + "(최종)",
        "birth": generate_random_birth(),
        "gender": "여성" if new_list_values["gender"] == "남성" else "남성",
        "phone": "01098765432",
        "email": "test@medisolveai.com",
    }

    page.fill('[data-testid="input_name"]', new_detail_values["customer_name"])
    page.fill('[data-testid="input_birth"]', new_detail_values["birth"])
    page.locator('[data-testid="drop_gender"]').select_option(label=new_detail_values["gender"])
    page.fill('[data-testid="input_phone"]', new_detail_values["phone"])
    page.fill('[data-testid="input_email"]', new_detail_values["email"])
    page.locator('[data-testid="btn_confirm"]').click()
    page.locator('[data-testid="btn_yes"]').click()
    page.wait_for_timeout(5000)

    # ✅ 고객관리 리스트 수정 확인
    page.goto(URLS["cen_customer"])
    page.fill('[data-testid="input_search_phone"]', new_detail_values["phone"])
    page.click("body")
    page.wait_for_timeout(3000)
    row = page.locator("table tbody tr").first
    row_text = row.inner_text()
    assert new_detail_values["customer_name"] in row_text
    assert new_detail_values["email"] in row_text

    # ✅ 예약관리 리스트 수정 확인
    page.goto(URLS["cen_reservation"])
    page.fill('[data-testid="input_search_phone"]', new_detail_values["phone"])
    page.click("body")
    page.wait_for_timeout(3000)
    row = page.locator("table tbody tr").first
    row_text = row.inner_text()
    assert new_detail_values["customer_name"] in row_text
    assert new_detail_values["email"] in row_text
    print(f"예약관리에서 고객 정보 확인 완료: {new_detail_values['customer_name']}")

    # ✅ 마이페이지 > 회원정보 확인 (로그인 상태 가정)
    page.goto(URLS["mypage_info"])
    page.wait_for_selector('[data-testid="mypage_user_name"]')
    expect(page.locator('[data-testid="mypage_user_name"]')).to_have_text(new_detail_values["customer_name"])
    expect(page.locator('[data-testid="mypage_user_phone"]')).to_have_text(new_detail_values["phone"])
    expect(page.locator('[data-testid="mypage_user_email"]')).to_have_text(new_detail_values["email"])
    print(f"마이페이지에서 회원정보 확인 완료: {new_detail_values['customer_name']}")

    print(f"✅ 최종 수정 완료 및 반영 확인: {new_detail_values['customer_name']}")

    # ✅ JSON 업데이트
    update_customer_in_json(customer["customer_name"], new_detail_values)
