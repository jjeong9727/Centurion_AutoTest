from playwright.sync_api import Page
from helpers.auth_helper import ensure_valid_token
from config import URLS

# 고객명과 멤버십 잔액 확인
def verify_membership_balance(page: Page, expected_customer_name: str, expected_balance: int):
    # 1. 홈페이지 메인 진입
    page.goto(URLS["home_main"])
    # 2. 로그인 토큰 주입
    access_token = ensure_valid_token()
    page.context.add_cookies([{
        "name": "access_token",
        "value": access_token,
        "domain": "your-domain.com",  # 테스트 서버 도메인
        "path": "/",
        "httpOnly": True,
        "secure": True,
        "sameSite": "Lax"
    }])
    page.reload()  # 토큰 적용 후 페이지 새로고침
    # 3. 마이페이지 버튼 클릭
    page.click("[data-testid='btn_mypage']")
    page.wait_for_load_state("networkidle")  # 페이지 완전히 로드 대기
    # 4. 고객명 읽어오기
    actual_customer_name = page.locator("[data-testid='txt_customer']").inner_text().strip()
    # 5. 멤버십 잔액 읽어오기
    actual_balance_text = page.locator("[data-testid='num_balance']").inner_text().strip()
    actual_balance = int(actual_balance_text.replace(",", ""))  # 쉼표 제거 후 정수 변환
    # 6. 검증
    assert actual_customer_name == expected_customer_name, f"❌ 고객명이 다릅니다. 예상: {expected_customer_name}, 실제: {actual_customer_name}"
    assert actual_balance == expected_balance, f"❌ 멤버십 금액이 다릅니다. 예상: {expected_balance}, 실제: {actual_balance}"
    print("✅ 고객명과 멤버십 잔액이 모두 일치합니다.")


# 외부 링크 이동 확인
def verify_popup_link(page, testid: str):
    locator = page.locator(f'[data-testid={testid}]')

    with page.expect_popup() as popup_info:
        locator.click(timeout=3000)

    new_page = popup_info.value
    new_page.wait_for_load_state()

    expected_url = URLS[testid]
    actual_url = new_page.url
    assert actual_url == expected_url, f"❌ URL 불일치: {actual_url} != {expected_url}"
    
    new_page.close()
# 호출 시 verify_popup_link(page, testid)

# 
