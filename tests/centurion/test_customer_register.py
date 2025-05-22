import random
from playwright.sync_api import Page, expect
from config import URLS
from helpers.customer_utils import (generate_random_customer, add_customer_to_json)

#내국인 등록 
def test_register_korean_customer(page: Page):
    page.goto(URLS["cen_cust_register"])

    # 랜덤 고객 데이터 생성
    customer = generate_random_customer()

    page.fill('[data-testid="input_name"]', customer["customer_name"])
    page.fill('[data-testid="input_birth"]', customer["birth"])
    page.locator('[data-testid="drop_gender"]').select_option(label=customer["gender"])
    page.fill('[data-testid="input_phone"]', customer["phone"])
    page.fill('[data-testid="input_email"]', "TEST") # 유효성 체크용 데이터

    # 국적 확인: 자동 '한국인' + 비활성화 상태
    nation_dropdown = page.locator('[data-testid="drop_nation"]')
    assert nation_dropdown.input_value() == "한국인", "❌ 국적은 '한국인'이어야 함"
    expect(nation_dropdown).to_be_disabled()
    print("✅ 국적 자동 설정 및 비활성화 확인")

    # 방문경로: 랜덤 선택
    path_dropdown = page.locator('[data-testid="drop_path"]')
    options = path_dropdown.locator("option")
    count = options.count()
    random_index = random.randint(0, count - 1)
    path_dropdown.select_option(index=random_index)

    if random_index == count - 1:  # 마지막 항목 = '기타'
        page.fill('[data-testid="input_path"]', "수기 입력 테스트")
        print("✅ 방문경로 기타 선택 → 수기입력 완료")
    else:
        selected_label = options.nth(random_index).inner_text().strip()
        print(f"✅ 방문경로 '{selected_label}' 선택 완료")

    # 완료 버튼 클릭
    page.locator('[data-testid="btn_confirm"]').click()
    expect(page.locator('[data-testid="toast_email"]')).to_be_visible(timeout=3000)
    print("✅ 이메일 형식 오류 유효성 검사 통과 (toast_email 확인됨)")

    # 올바른 이메일 재입력
    page.fill('[data-testid="input_email"]', customer["email"])

    # 완료 버튼 클릭 (성공)
    page.locator('[data-testid="btn_confirm"]').click()
    expect(page.locator('[data-testid="toast_confirm"]')).to_be_visible(timeout=3000)
    print(f"✅ 고객 등록 완료: {customer['customer_name']}")


#외국인 등록
def test_register_foreign_customer(page: Page):
    page.goto(URLS["cen_cust_register"])

    # 랜덤 고객 데이터 생성
    customer = generate_random_customer()

    # 유형: 외국인 선택
    page.locator('[data-testid="drop_type"]').select_option(label="외국인")
    print("✅ 유형 외국인 선택 완료")

    # 기본 정보 입력
    page.fill('[data-testid="input_name"]', customer["customer_name"])
    page.fill('[data-testid="input_birth"]', customer["birth"])
    page.locator('[data-testid="drop_gender"]').select_option(label=customer["gender"])
    page.fill('[data-testid="input_phone"]', customer["phone"])
    page.fill('[data-testid="input_email"]', customer["email"])

    # 국적 드롭다운에서 랜덤 선택
    nation_dropdown = page.locator('[data-testid="drop_nation"]')
    options = nation_dropdown.locator("option")
    count = options.count()
    random_index = random.randint(0, count - 1)
    nation_dropdown.select_option(index=random_index)
    selected_nation = options.nth(random_index).inner_text().strip()
    print(f"✅ 국적 선택 완료: {selected_nation}")
    customer["nation"] = selected_nation  # JSON 저장용

    # 방문경로: 랜덤 선택
    path_dropdown = page.locator('[data-testid="drop_path"]')
    path_options = path_dropdown.locator("option")
    path_count = path_options.count()
    path_index = random.randint(0, path_count - 1)
    path_dropdown.select_option(index=path_index)

    if path_index == path_count - 1:  # '기타'
        page.fill('[data-testid="input_path"]', "수기 입력 테스트")
        print("✅ 방문경로 기타 선택 → 수기입력 완료")
    else:
        selected_path = path_options.nth(path_index).inner_text().strip()
        print(f"✅ 방문경로 '{selected_path}' 선택 완료")

    # 완료 버튼 클릭
    page.locator('[data-testid="btn_confirm"]').click()

    # 등록 완료 확인
    expect(page.locator('[data-testid="toast_confirm"]')).to_be_visible(timeout=3000)
    print(f"✅ 외국인 고객 등록 완료: {customer['customer_name']}")

    # JSON 저장
    add_customer_to_json(customer)

