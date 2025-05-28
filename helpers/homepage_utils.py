from playwright.sync_api import Page
from helpers.auth_helper import ensure_valid_token
from config import URLS
from datetime import datetime, timedelta

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


# 예약 정보 생성 (날짜 선택 기준)
def get_reservation_datetime():
    now = datetime.now()
    if now.day > 20:
        target_date = (now.replace(day=1) + timedelta(days=32)).replace(day=1)
        use_next_month = True
    else:
        target_date = now + timedelta(days=1)
        use_next_month = False

    return {
        "date": target_date.strftime("%Y-%m-%d"),
        "day": target_date.day,
        "month": target_date.month,
        "use_next_month": use_next_month,
    }
# 예약 정보 생성 (시간 선택 기준)
def get_available_time_button(page: Page):
    now = datetime.now()
    time_buttons = page.locator("[data-testid^='btn_time_']")
    for i in range(time_buttons.count()):
        btn = time_buttons.nth(i)
        if btn.is_enabled():
            time_value = btn.get_attribute("data-testid").split("_")[-1]
            hour, minute = int(time_value[:2]), int(time_value[2:])
            time_obj = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if time_obj > now:
                return btn, f"{hour:02}:{minute:02}"
    raise Exception("선택 가능한 미래 시간이 없습니다")