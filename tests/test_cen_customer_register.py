# 테스트 흐름
# 1. 한국인 / 외국인 정보 생성
# 2. 한국인 등록 시 이메일 유효성 체크 후 버튼 활성화 까지 진행
# 3. 외국인 등록 시 전화번호or이메일 중복 체크(한국인 정보 활용) 및 이메일 유효성 체크 까지만 진행
import random
from playwright.sync_api import Page, expect
from config import URLS
from helpers.customer_utils import (generate_random_customer, add_customer_to_json, cen_login)

def test_register_customer(page: Page):
    cen_login(page) # 로그인 

    page.goto(URLS["cen_customer"])

    # ✅ 고객 정보 두 세트 미리 생성
    korean_customer = generate_random_customer()
    foreign_customer = generate_random_customer()

    # ✅ 내국인 등록
    page.locator('[data-testid="btn_register_cus"]').click()
    page.wait_for_timeout(2000)
    page.fill('[data-testid="input_name"]', korean_customer["customer_name"])
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_gender"]').click()
    page.wait_for_timeout(1000)
    page.get_by_role("option", name=korean_customer["gender"]).click()
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_phone"]', korean_customer["phone"])
    page.wait_for_timeout(1000)

    # 7자리 생년월일 입력 후 완료 버튼 비활성화 확인
    page.fill('[data-testid="input_email"]', korean_customer["email"])
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_birth"]', "1989070") # 7자리 입력
    page.wait_for_timeout(1000)

    # 잘못된 생년월일 입력 후 완료 클릭 → 유효성 팝업 확인 
    page.fill('[data-testid="input_birth"]', "19190101") # 년도 오류 
    page.wait_for_timeout(1000)
    page.locator('body').click()
    page.locator('[data-testid="btn_confirm"]').click()
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_birth"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    page.fill('[data-testid="input_birth"]', "19201301") # 월 오류 
    page.wait_for_timeout(1000)    
    page.locator('body').click()
    page.locator('[data-testid="btn_confirm"]').click()
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_birth"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    page.fill('[data-testid="input_birth"]', "19200132") # 일 오류 
    page.wait_for_timeout(1000)
    page.locator('body').click()
    page.locator('[data-testid="btn_confirm"]').click()
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_birth"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    # 정상 생년월일 입력 및 이메일 초기화
    page.fill('[data-testid="input_birth"]', korean_customer["birth"])
    page.wait_for_timeout(1000)
    page.locator('body').click()
    page.fill('[data-testid="input_email"]', "")
    page.wait_for_timeout(1000)
    

    # 잘못된 이메일 입력 후 완료 클릭 → 유효성 팝업 확인
    page.fill('[data-testid="input_email"]', "TEST")
    page.wait_for_timeout(1000)
    page.locator('body').click()
    page.locator('[data-testid="btn_confirm"]').click()
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_email"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    print("✅ 이메일 형식 오류 토스트 확인")

    # 정상 이메일 입력
    page.fill('[data-testid="input_email"]', korean_customer["email"])
    page.wait_for_timeout(1000)
    page.locator('body').click()

   
    expect(page.locator('[data-testid="drop_nation"]')).to_be_disabled()
    print("✅ 국적 자동 설정 및 비활성화 확인")

    # 방문경로 랜덤 선택 
    page.locator('[data-testid="drop_path"]').click()
    page.wait_for_timeout(1000)
    path_options = page.locator("div[role='option']")
    path_count = path_options.count()
    path_index = random.randint(0, path_count - 1)
    path_options.nth(random_index).click()
    page.wait_for_timeout(1000)

    
    expect(page.locator('[data-testid="btn_confirm]')).to_be_enabled()
    page.wait_for_timeout(1000)

    print("✅ 내국인 고객 추가 유효성 확인")
    
    page.locator('[data-testid="btn_confirm"]').click()
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_confirm"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    print(f"✅ 내국인 고객 등록 완료: {korean_customer['customer_name']}")

    # 고객 정보 별도 저장 하지 않음 
    # add_customer_to_json(korean_customer) 


    # ✅ 외국인 등록 시도 (중복 연락처/이메일 사용)
    page.goto(URLS["cen_customer"])
    page.wait_for_timeout(1000)
    page.locator('[data-testid="btn_register_cus"]').click()
    page.wait_for_timeout(2000)
    
    page.locator('[data-testid="drop_type"]').select_option(label="외국인")
    page.wait_for_timeout(1000)
    print("✅ 유형 외국인 선택 완료")

    page.fill('[data-testid="input_name"]', foreign_customer["customer_name"])
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_birth"]', foreign_customer["birth"])
    page.wait_for_timeout(1000)
    page.locator('[data-testid="drop_gender"]').click()
    page.wait_for_timeout(1000)
    page.get_by_role("option", name=korean_customer["gender"]).click()
    page.wait_for_timeout(1000)


    # 중복된 이메일(외국인)만 적용
    # page.fill('[data-testid="input_phone"]', korean_customer["phone"])
    page.fill('[data-testid="input_email"]', korean_customer["email"])
    page.wait_for_timeout(1000)

    nation_dropdown = page.locator('[data-testid="drop_nation"]')
    nation_dropdown.click()
    page.wait_for_timeout(1000)

    options = page.locator("option")
    count = options.count()
    random_index = random.randint(0, count - 1)

    # 실제 select 대상은 숨겨진 <select>라면 select_option 사용, 아니면 option 클릭
    nation_dropdown.select_option(index=random_index)
    selected_nation = options.nth(random_index).inner_text().strip()
    foreign_customer["nation"] = selected_nation
    print(f"✅ 외국인 국적 선택: {selected_nation}")

    # 방문경로 랜덤 선택 
    page.locator('[data-testid="drop_path"]').click()
    page.wait_for_timeout(1000)
    path_options = page.locator("div[role='option']")
    path_count = path_options.count()
    path_index = random.randint(0, path_count - 1)
    path_options.nth(random_index).click()
    page.wait_for_timeout(1000)

    # 중복 등록 시도
    page.locator('[data-testid="btn_confirm"]').click()
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_duplicate"]')).to_be_visible(timeout=3000)
    print("✅ 중복 등록 토스트 확인 완료")

    # 잘못된 이메일 재입력 후 유효성 확인
    page.fill('[data-testid="input_email"]', "TEST")
    page.wait_for_timeout(1000)
    page.locator('body').click()
    page.locator('[data-testid="btn_confirm"]').click()
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_email"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    print("✅ 외국인 이메일 유효성 오류 확인")

    # 외국인 정보로 재입력 후 버튼 활성화 확인
    page.fill('[data-testid="input_phone"]', foreign_customer["phone"])
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_email"]', foreign_customer["email"])
    page.wait_for_timeout(1000)
    page.locator('body').click()
    expect(page.locator('[data-testid="btn_confirm]')).to_be_enabled()
    page.wait_for_timeout(1000)
    print("✅ 외국인 고객 추가 유효성 확인")

    page.locator('[data-testid="btn_confirm"]').click()
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_confirm"]')).to_be_visible(timeout=3000)
    print(f"✅ 외국인 고객 등록 완료: {foreign_customer['customer_name']}")

    # 고객 정보 별도 저장 하지 않음 
    # add_customer_to_json(foreign_customer)
