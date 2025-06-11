# 멤버십 충전 차감 테스트
# 고객 선택 후 고객 정보 자동 기입 확인
# 미입력 toast 확인
# 차감 시 금액 부족 toast 확인
# 충전/차감 후 반영 확인

import json
from playwright.sync_api import Page, expect
from helpers.customer_utils import update_customer_in_json, cen_login
from config import URLS

CUSTOMER_FILE = "data/customers.json"

def load_one_customer():
    with open(CUSTOMER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)[0]

# charge_ : 충전 금액 | expected_ : 보유 금액 | 
def test_membership_charge_and_deduct(page: Page):
    customer = load_one_customer()
    assert customer, "❌ 고객 정보가 필요합니다."

    cen_login(page) # 로그인인
    page.goto(URLS["cen_customer"])
    page.wait_for_timeout(2000)

    # 멤버십 충전/차감 버튼 클릭
    page.click('[data-testid="btn_register_mem"]')
    page.wait_for_timeout(2000)

    # 완료 버튼 비활성화 확인
    expect(page.locator('[data-testid="btn_yes"]')).to_be_disabled()

    # 고객 선택 (drop 검색 후 선택)
    page.click('[data-testid="drop_name_trigger"]')
    page.fill('[data-testid="drop_name_search"]', customer["customer_name"])
    page.locator('[data-testid="drop_name_item"]', has_text=customer["customer_name"]).first.click()

    # 고객명/등급 자동 입력 확인
    expect(page.locator('[data-testid="drop_name_trigger"]')).to_have_text(customer["customer_name"])
    expect(page.locator('[data-testid="drop_grade"]')).to_have_text(customer["grade"])

    # 미입력 상태에서 완료 클릭 → 토스트 확인
    page.click('[data-testid="btn_yes"]')
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_amount"]')).to_be_visible()
    page.wait_for_timeout(3000)

    # 금액/매일리지 입력
    charge_amount = 50000
    charge_mileage = 300

    page.fill('[data-testid="input_amount_mem"]', str(charge_amount))
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_amount_mile"]', str(charge_mileage))
    page.wait_for_timeout(1000)

    # 메모 입력
    page.fill('[data-testid="input_memo"]', "자동화 테스트 충전")
    page.wait_for_timeout(1000)

    # 완료 클릭 → 목록에서 확인
    page.click('[data-testid="btn_yes"]')
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_nocharge"]')
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_yes"]')
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_charge"]')
    page.wait_for_timeout(500)

    expect(page.locator('[data-testid="toast_charge"]')).to_be_visible()
    page.wait_for_timeout(1000)

    # 보유 멤버십 / 마일리지 확인 
    page.click('[data-testid="btn_register_mem"]')
    page.wait_for_timeout(2000)
    page.click('[data-testid="type_deduct"]')
    page.wait_for_timeout(1000)

    page.click('[data-testid="drop_name_trigger"]')
    page.wait_for_timeout(2000)
    page.fill('[data-testid="drop_name_search"]', customer["customer_name"])
    page.wait_for_timeout(2000)
    page.locator('[data-testid="drop_name_item"]', has_text=customer["customer_name"]).first.click()
    page.wait_for_timeout(2000)

    expected_amount = customer.get("amount", 0) + charge_amount
    expected_mileage = customer.get("mileage", 0) + charge_mileage
    charged_total = charge_amount + charge_mileage
    previous_charged = customer.get("charged", 0)
    new_charged = previous_charged + charged_total

    mem_text = page.locator('[data-testid="num_mem"]').inner_text()
    mile_text = page.locator('[data-testid="num_mile"]').inner_text()

    mem = int(mem_text.replace(",", "").strip())
    mile = int(mile_text.replace(",", "").strip())

    assert mem == expected_amount, f"❌ 보유 금액 불일치: {mem} != {expected_amount}"
    assert mile == expected_mileage, f"❌ 보유 마일리지 불일치: {mile} != {expected_mileage}"
    print(f"✅ 보유 금액/마일리지 정산 확인: {mem} / {mile}")

    updated = {
        **customer,
        "amount": expected_amount,
        "mileage": expected_mileage,
        "charged": new_charged
    }
    update_customer_in_json(customer["customer_name"], updated)

    # 차감 테스트
    page.fill('[data-testid="input_amount_mem"]', str(expected_amount + 1000))
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_amount_mile"]', str(expected_mileage + 1000))
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_yes"]')
    page.wait_for_timeout(500)

    expect(page.locator('[data-testid="toast_amount"]')).to_be_visible()
    page.wait_for_timeout(1000)

    expect(page.locator('[data-testid="input_amount_mem"]')).to_have_value(str(expected_amount))
    page.wait_for_timeout(1000)
    expect(page.locator('[data-testid="input_amount_mile"]')).to_have_value(str(expected_mileage))
    page.wait_for_timeout(1000)

    deducted_amount = expected_amount - 100
    deducted_mileage = expected_mileage - 100
    page.fill('[data-testid="input_amount_mem"]', str(deducted_amount))
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_amount_mile"]', str(deducted_mileage))
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_memo"]', "자동화 테스트 차감")
    page.wait_for_timeout(1000)

    page.click('[data-testid="btn_yes"]')
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_nodeduct"]')
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_yes"]')
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_deduct"]')
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_deduct"]')).to_be_visible()
    page.wait_for_timeout(2000)

    # 차감 후 결과 확인
    page.goto(URLS["cen_customer"])
    page.fill('[data-testid="input_search_phone"]', customer["phone"])
    page.wait_for_timeout(1000)
    page.click("body")
    page.wait_for_timeout(3000)
    row = page.locator("table tbody tr").first
    row.locator("td").nth(6).click()
    page.wait_for_timeout(2000)
    page.locator('[data-testid="btn_review"]').click()
    page.wait_for_timeout(2000)

    before_amount = expected_amount
    before_mileage = expected_mileage
    balance_amount = before_amount - deducted_amount
    balance_mileage = before_mileage - deducted_mileage
    expected_total = balance_amount + balance_mileage # 보유 금액(멤버십+마일리지)

    page.click('[data-testid="tab_membership"]')
    page.wait_for_timeout(2000)

    row = page.locator("table tbody tr").first
    cells = row.locator("td")

    membership_amount_text = cells.nth(1).inner_text()
    mileage_amount_text = cells.nth(2).inner_text()
    total_amount_text = cells.nth(3).inner_text()

    mem = int(membership_amount_text.replace(",", "").strip())
    mile = int(mileage_amount_text.replace(",", "").strip())
    total = int(total_amount_text.replace(",", "").strip())

    assert mem == balance_amount, f"❌ 멤버십 금액 불일치: {mem} != {balance_amount}"
    assert mile == balance_mileage, f"❌ 마일리지 금액 불일치: {mile} != {balance_mileage}"
    assert total == expected_total, f"❌ 합산 금액 불일치: {total} != {expected_total}"
    print(f"✅ 차감 결과 일치: 멤버십 {mem} + 마일리지 {mile} = {total}")

    # 마이페이지 확인
    page.goto(URLS["home_mypage_pc"])
    page.wait_for_timeout(3000)

    total_balance = total
    total_charged = updated["charged"]

    expected_display = f"{total_balance:,} / {total_charged:,}"
    displayed_text = page.locator('[data-testid="membership_status"]').inner_text()

    assert expected_display == displayed_text, \
        f"❌ 마이페이지 멤버십 정보 불일치: 기대값={expected_display}, 실제값={displayed_text}"
    print(f"✅ 마이페이지 멤버십 확인: {displayed_text}")
    print(f"✅ 멤버십 충전/차감 테스트 완료: {updated['customer_name']}")
