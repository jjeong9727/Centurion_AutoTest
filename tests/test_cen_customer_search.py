# 테스트 흐름
# 1. 검색 전 노출되는 항목의 개수 저장 
# 2. 검색 각 항목 입력 후 검색 결과 노출 확인 (검색 결과 1개 되도록)
# 3. 초기화 버튼 선택 시 입력 필드 삭제 및 검색결과 초기화(검색 전 노출 항목의 개수)

import json
import random
from config import URLS
from playwright.sync_api import Page, expect
from helpers.customer_utils import cen_login

CUSTOMER_FILE = "data/customers.json"
# def load_customer(email: str = "jekwon@medisolveai.com"):
def load_customer(phone: str = "01062754153"):
    import json

    with open(CUSTOMER_FILE, "r", encoding="utf-8") as f:
        customers = json.load(f)

    for cust in customers:
        if cust.get("phone") == phone:
            return cust

    raise ValueError(f"⚠️ 전화번호 {phone}에 해당하는 고객 정보를 찾을 수 없습니다.")
def test_search_field(page: Page):
    cen_login(page) #로그인 

    page.goto(URLS["cen_customer"])
    page.wait_for_timeout(2000)

    # 초기 노출된 고객 리스트 수 저장
    initial_count = page.locator("table tbody tr").count()
    cust = load_customer()

    # 1. 고객명 검색 → 확인 → 초기화
    page.fill('[data-testid="input_search_name"]', cust["name"])
    page.wait_for_timeout(1000)
    page.click("body")
    page.wait_for_timeout(1000)

    first_row = page.locator("table tbody tr").first
    name_cell = first_row.locator("td").nth(1)

    # ✅ 줄바꿈 기준 앞 텍스트만 비교
    main_text = name_cell.inner_text().strip().split("\n")[0]
    assert main_text == cust["name"], f"❌ 이름 불일치: '{main_text}' != '{cust['name']}'"

    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_reset"]')
    page.wait_for_timeout(2000)

    # 2. 생년월일 검색 → 확인 → 초기화
    page.fill('[data-testid="input_search_birth"]', cust["birth"])
    page.wait_for_timeout(1000)
    page.click("body")
    page.wait_for_timeout(1000)
    first_row = page.locator("table tbody tr").first
    birth_cell = first_row.locator("td").nth(2)
    formatted_birth = f"{cust['birth'][:4]}.{cust['birth'][4:6]}.{cust['birth'][6:]}"
    expect(birth_cell).to_have_text(formatted_birth)
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_reset"]')
    page.wait_for_timeout(2000)
    # 3. 성별 검색 → 확인 → 초기화
    page.locator('[data-testid="drop_search_gender_trigger"]').click()
    page.get_by_role("option", name=cust["gender"]).click()
    page.wait_for_timeout(1000)
    page.click("body")
    page.wait_for_timeout(1000)
    first_row = page.locator("table tbody tr").first
    gender_cell = first_row.locator("td").nth(3)

    # ✅ 로그 출력 추가
    actual_gender = gender_cell.inner_text().strip()
    expected_gender = cust["gender"]
    expect(gender_cell).to_have_text(cust["gender"])
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_reset"]')
    page.wait_for_timeout(2000)
    
    # 4. 전화번호 검색 → 확인 → 초기화
    page.fill('[data-testid="input_search_phone"]', cust["phone"])
    page.wait_for_timeout(1000)
    page.click("body")
    page.wait_for_timeout(1000)

    first_row = page.locator("table tbody tr").first
    phone_cell = first_row.locator("td").nth(4)

    # ✅ 하이픈 포맷 처리 (01012345678 → 010-1234-5678)
    raw_phone = cust["phone"]
    expected_phone = f"{raw_phone[:3]}-{raw_phone[3:7]}-{raw_phone[7:]}"
    actual_phone = phone_cell.inner_text().strip()

    assert actual_phone == expected_phone, f"❌ 전화번호 불일치: '{actual_phone}' != '{expected_phone}'"

    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_reset"]')
    page.wait_for_timeout(2000)

    # 5. 국적 검색 → 확인 → 초기화
    page.locator('[data-testid="drop_search_nation_trigger"]').last.click()
    page.get_by_role("option", name=cust["nationality"]).click()
    page.click("body")
    page.wait_for_timeout(1000)
    first_row = page.locator("table tbody tr").first
    nation_cell = first_row.locator("td").nth(6)
    expect(nation_cell).to_have_text(cust["nationality"])
    page.wait_for_timeout(2000)

    # 6. 최종적으로 고객 리스트 수 복원 확인
    page.click('[data-testid="btn_reset"]')
    page.wait_for_timeout(2000)
    expect(page.locator("table tbody tr")).to_have_count(initial_count)
    print(f"✅ 모든 단일 조건 검색 후 초기화 성공 / 복원된 고객 수: {initial_count}")
