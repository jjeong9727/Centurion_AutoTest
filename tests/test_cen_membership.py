# 멤버십 충전 차감 테스트
# 고객 선택 후 고객 정보 자동 기입 확인
# 미입력 toast 확인
# 차감 시 금액 부족 toast 확인
# 충전/차감 후 반영 확인 및 최종 잔액 JSON 저장 + 국적별 로그인 분기

import json
from playwright.sync_api import Page, expect
from helpers.customer_utils import update_customer_in_json, cen_login
from helpers.auth_helper import login_with_token
from config import URLS

CUSTOMER_FILE = "data/customers.json"

def load_one_customer():
    with open(CUSTOMER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)[0]

def test_membership_charge_and_deduct(page: Page):
    customer = load_one_customer()
    assert customer, "❌ 고객 정보가 필요합니다."

    cen_login(page)
    page.goto(URLS["cen_customer"])
    page.wait_for_timeout(2000)

    # 메머식 충전
    page.click('[data-testid="btn_register_mem"]')
    page.wait_for_timeout(2000)
    expect(page.locator('[data-testid="btn_yes"]')).to_be_disabled()

    page.click('[data-testid="drop_name_trigger"]')
    page.wait_for_timeout(1000)
    page.fill('[data-testid="drop_name_search"]', customer["name"])
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_name_item"]', has_text=customer["name"]).first.click()
    page.wait_for_timeout(2000)

    expect(page.locator('[data-testid="drop_name_trigger"]')).to_have_text(customer["name"])
    expect(page.locator('[data-testid="drop_grade"]')).to_have_text(customer["grade"])

    page.click('[data-testid="btn_yes"]')
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_amount"]')).to_be_visible()
    page.wait_for_timeout(3000)

    charge_amount, charge_mileage = 50000, 300
    page.fill('[data-testid="input_amount_mem"]', str(charge_amount))
    page.fill('[data-testid="input_amount_mile"]', str(charge_mileage))
    page.fill('[data-testid="input_memo"]', "자동화 테스트 충전")

    page.click('[data-testid="btn_yes"]')
    page.click('[data-testid="btn_nocharge"]')
    page.click('[data-testid="btn_yes"]')
    page.click('[data-testid="btn_charge"]')
    expect(page.locator('[data-testid="toast_charge"]')).to_be_visible()

    # 최종 계산
    expected_amount = customer.get("amount", 0) + charge_amount
    expected_mileage = customer.get("mileage", 0) + charge_mileage
    new_charged = customer.get("charged", 0) + charge_amount + charge_mileage

    # 차감 테스트 (limit 초과 → 실패 후 적절 금액으로 성공)
    page.click('[data-testid="btn_register_mem"]')
    page.click('[data-testid="type_deduct"]')
    page.click('[data-testid="drop_name_trigger"]')
    page.fill('[data-testid="drop_name_search"]', customer["name"])
    page.locator('[data-testid="drop_name_item"]', has_text=customer["name"]).first.click()

    page.fill('[data-testid="input_amount_mem"]', str(expected_amount + 1000))
    page.fill('[data-testid="input_amount_mile"]', str(expected_mileage + 1000))
    page.click('[data-testid="btn_yes"]')
    expect(page.locator('[data-testid="toast_amount"]')).to_be_visible()

    deducted_amount = expected_amount - 100
    deducted_mileage = expected_mileage - 100
    page.fill('[data-testid="input_amount_mem"]', str(deducted_amount))
    page.fill('[data-testid="input_amount_mile"]', str(deducted_mileage))
    page.fill('[data-testid="input_memo"]', "자동화 테스트 차감")

    page.click('[data-testid="btn_yes"]')
    page.click('[data-testid="btn_nodeduct"]')
    page.click('[data-testid="btn_yes"]')
    page.click('[data-testid="btn_deduct"]')
    expect(page.locator('[data-testid="toast_deduct"]')).to_be_visible()

    # 차감 후 계산
    balance_amount = expected_amount - deducted_amount
    balance_mileage = expected_mileage - deducted_mileage
    final_total = balance_amount + balance_mileage

    final_updated = {
        **customer,
        "amount": balance_amount,
        "mileage": balance_mileage,
        "charged": new_charged
    }
    update_customer_in_json(customer["name"], final_updated)

    # 국적에 따라 로그인 방식 분기
    account_type = "kakao" if customer.get("nationality") == "한국인" else "google"
    login_with_token(page, account_type=account_type)

    page.goto(URLS["home_mypage_mem"])
    page.wait_for_timeout(3000)

    expected_display = f"{final_total:,} / {new_charged:,}"
    displayed_text = page.locator('[data-testid="membership_status"]').inner_text()

    assert displayed_text == expected_display, \
        f"❌ 마이페이지 메머식 계산 불일치: {displayed_text} != {expected_display}"
    print(f"✅ 마이페이지 메머식 확인 완료: {displayed_text}")
