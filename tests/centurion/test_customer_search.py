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

def test_customer_search_and_reset(page: Page):
    page.goto(URLS["cen_customer"])  # URL은 실제 경로로 대체

    # 1. 초기 노출된 고객 리스트 수 저장
    initial_count = page.locator("table tbody tr").count()

    # 2. 랜덤 고객 정보 로딩
    cust = load_random_customer()

    # 3. 검색 항목 입력 및 자동 검색 (포커스 아웃)
    page.fill('[data-testid="input_search_name"]', cust["customer_name"])
    # page.locator("body").click()
    page.blur()
    page.fill('[data-testid="input_search_birth"]', cust["birth"])
    page.blur()
    page.locator('[data-testid="drop_search_gender"]').select_option(label=cust["gender"])
    page.blur()
    page.fill('[data-testid="input_search_phone"]', cust["phone"])
    page.blur()
    page.locator('[data-testid="drop_search_nation"]').select_option(label=cust["nation"])
    page.blur()

    # 4. 검색 결과 1건 확인
    expect(page.locator("table tbody tr")).to_have_count(1)

    # 5. 고객명에 숫자 추가 → 검색 안됨 확인
    page.fill('[data-testid="input_search_name"]', cust["customer_name"] + "12345")
    page.blur()
    expect(page.locator('[data-testid="txt_noresult"]')).to_be_visible()

    # 6. 초기화 버튼 클릭
    page.click('[data-testid="btn_reset"]')

    # 7. 입력 필드 초기화 확인
    expect(page.locator('[data-testid="input_search_name"]')).to_have_attribute("value", "")
    expect(page.locator('[data-testid="input_search_birth"]')).to_have_attribute("value", "")
    expect(page.locator('[data-testid="drop_search_gender"]')).to_have_value("")
    expect(page.locator('[data-testid="input_search_phone"]')).to_have_attribute("value", "")
    expect(page.locator('[data-testid="drop_search_nation"]')).to_have_value("")

    # 8. 초기 고객 리스트 수 복원 확인
    expect(page.locator("table tbody tr")).to_have_count(initial_count)
    print(f"✅ 초기화 후 고객 리스트 정상 복원: {initial_count}건")
