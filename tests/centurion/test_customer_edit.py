# 테스트 흐름
# 1. 등록된 고객 정보 불러와 [고객명] 기준 검색
# 2. 리스트 > 상세 > 수정모드 진입 -> 이탈 시 Alert 확인
# 3. [고객명] 다시 검색 수정 화면 바로 진입
# 4. 일부 데이터 수정 후 저장 -> 리스트에 반영 확인

import json
import random
from playwright.sync_api import Page, expect
from helpers.customer_utils import (generate_random_birth, generate_random_phone, generate_random_email, update_customer_in_json)

CUSTOMER_FILE = "data/customers.json"


def load_two_customers():
    with open(CUSTOMER_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data[:2] if len(data) >= 2 else None

def test_edit_customer_list_and_detail(page: Page):
    customers = load_two_customers()
    assert customers and len(customers) == 2, "❌ 수정 대상 고객 2명이 필요합니다."

    list_target, detail_target = customers[0], customers[1]

    # ========== 리스트에서 셀 수정 ==========
    page.goto("/고객관리")
    page.fill('[data-testid="input_search_phone"]', list_target["phone"])
    # page.locator("body").click()
    page.blur()
    row = page.locator("table tbody tr").first
    cells = row.locator("td")

    # 2~6열: 고객명/생년월일/성별/전화번호/이메일
    fields = ["customer_name", "birth", "gender", "phone", "email"]
    new_values = {
        "customer_name": list_target["customer_name"].replace("자동화", "수정됨"),
        "birth": generate_random_birth(),
        "gender": "여성" if list_target["gender"] == "남성" else "남성",
        "phone": generate_random_phone(),
        "email": generate_random_email(),
    }

    for i, key in enumerate(fields):
        cell = cells.nth(i + 1)  # 2~6열
        cell.click()
        if key == "gender":
            page.locator("select").select_option(label=new_values[key])
        else:
            input_box = page.locator("input").first
            input_box.fill("")
            page.blur()
            expect(page.locator('[data-testid="toast_required"]')).to_be_visible()
            input_box.fill(new_values[key])
            page.blur()

    update_customer_in_json(list_target["customer_name"], new_values)

    # ========== 상세 진입 후 수정 ==========
    page.fill('[data-testid="input_search_phone"]', detail_target["phone"])
    page.locator("body").click()
    page.wait_for_timeout(3000)
    # 상세 진입 후 수정 모드 
    row = page.locator("table tbody tr").first
    row.locator("td").nth(6).click()
    page.wait_for_timeout(3000)
    page.locator('[data-testid="btn_review"]').click()
    page.wait_for_timeout(3000)
    page.locator('[data-testid="btn_edit"]').click()
    page.wait_for_timeout(3000)
    # 화면 이탈 시 수정 미반영 확인
    page.go_back()
    page.wait_for_timeout(5000)
    page.locator('[data-testid="btn_yes"]').click()
    page.wait_for_timeout(8000)

    # 테스트 정보 재검색 후 수정 화면 진입 
    page.fill('[data-testid="input_search_phone"]', detail_target["phone"])
    page.locator("body").click()
    page.wait_for_timeout(5000)
    row = page.locator("table tbody tr").first
    row.locator("td").nth(6).click()
    page.wait_for_timeout(3000)
    page.locator('[data-testid="btn_edit"]').click()
    page.wait_for_timeout(5000)

    new_detail_values = {
        "customer_name": detail_target["customer_name"].replace("자동화", "수정됨"),
        "birth": generate_random_birth(),
        "phone": generate_random_phone(),
        "email": generate_random_email(),
    }

    page.fill('[data-testid="input_name"]', new_detail_values["customer_name"])
    page.wait_for_timeout(3000)
    page.fill('[data-testid="input_birth"]', new_detail_values["birth"])
    page.wait_for_timeout(3000)
    page.locator('[data-testid="drop_gender"]').select_option(label="여성" if detail_target["gender"] == "남성" else "남성")
    page.wait_for_timeout(3000)
    page.fill('[data-testid="input_phone"]', new_detail_values["phone"])
    page.wait_for_timeout(3000)
    page.fill('[data-testid="input_email"]', new_detail_values["email"])
    page.wait_for_timeout(3000)
    page.locator('[data-testid="btn_confirm"]').click()
    page.wait_for_timeout(3000)
    page.locator('[data-testid="btn_yes"]').click()
    page.wait_for_timeout(8000)

    update_customer_in_json(detail_target["customer_name"], new_detail_values)

    # ========== 최종 확인 ==========
    for customer in [new_values, new_detail_values]:
        page.fill('[data-testid="input_search_phone"]', customer["phone"])
        page.wait_for_timeout(1000)
        page.locator("body").click()
        page.wait_for_timeout(5000)
        row = page.locator("table tbody tr").first
        assert customer["customer_name"] in row.inner_text()
        assert customer["email"] in row.inner_text()
        print(f"✅ 고객 수정 확인 완료: {customer['customer_name']}")
