# 테스트 흐름
# 1. 검색 전 노출되는 항목의 개수 저장 
# 2. 검색 각 항목 입력 후 검색 결과 노출 확인 (검색 결과 1개 되도록)
# 3. 초기화 버튼 선택 시 입력 필드 삭제 및 검색결과 초기화(검색 전 노출 항목의 개수)

import json
import random
from config import URLS
from playwright.sync_api import Page, expect

CUSTOMER_FILE = "data/customers.json"

def load_random_customer():
    with open(CUSTOMER_FILE, "r", encoding="utf-8") as f:
        customers = json.load(f)
    return random.choice(customers)

def test_search_field(page: Page):
    page.goto(URLS["cen_customer"])
    page.wait_for_timeout(2000)

    # 초기 노출된 고객 리스트 수 저장
    initial_count = page.locator("table tbody tr").count()
    cust = load_random_customer()

    # 1. 고객명 검색 → 확인 → 초기화
    page.fill('[data-testid="input_search_name"]', cust["customer_name"])
    page.wait_for_timeout(1000)
    page.click("body")
    page.wait_for_timeout(1000)
    expect(page.locator("table tbody tr td").nth(1)).to_have_text(cust["customer_name"])
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_reset"]')
    page.wait_for_timeout(2000)

    # 2. 생년월일 검색 → 확인 → 초기화
    page.fill('[data-testid="input_search_birth"]', cust["birth"])
    page.wait_for_timeout(1000)
    page.click("body")
    page.wait_for_timeout(1000)
    expect(page.locator("table tbody tr td").nth(2)).to_have_text(cust["birth"])
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_reset"]')
    page.wait_for_timeout(2000)

    # 3. 성별 검색 → 확인 → 초기화
    page.locator('[data-testid="drop_search_gender"]').select_option(label=cust["gender"])
    page.wait_for_timeout(1000)
    page.click("body")
    page.wait_for_timeout(1000)
    expect(page.locator("table tbody tr td").nth(3)).to_have_text(cust["gender"])
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_reset"]')
    page.wait_for_timeout(2000)

    # 4. 전화번호 검색 → 확인 → 초기화
    page.fill('[data-testid="input_search_phone"]', cust["phone"])
    page.wait_for_timeout(1000)
    page.click("body")
    page.wait_for_timeout(1000)
    expect(page.locator("table tbody tr td").nth(4)).to_have_text(cust["phone"])
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_reset"]')
    page.wait_for_timeout(2000)

    # 5. 국적 검색 → 확인 → 초기화
    page.locator('[data-testid="drop_search_nation"]').select_option(label=cust["nation"])
    page.click("body")
    page.wait_for_timeout(1000)
    expect(page.locator("table tbody tr td").nth(6)).to_have_text(cust["nation"])
    page.wait_for_timeout(2000)

    # 6. 최종적으로 고객 리스트 수 복원 확인
    page.click('[data-testid="btn_reset"]')
    page.wait_for_timeout(2000)
    expect(page.locator("table tbody tr")).to_have_count(initial_count)
    print(f"✅ 모든 단일 조건 검색 후 초기화 성공 / 복원된 고객 수: {initial_count}")
