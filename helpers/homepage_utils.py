from playwright.sync_api import Page
from helpers.auth_helper import login_with_token
from config import URLS
from datetime import datetime
import random
import calendar

# 고객명과 멤버십 잔액 확인
def verify_membership_balance(page: Page, expected_customer_name: str, expected_balance: int):
    # 1. 홈페이지 메인 진입
    page.goto(URLS["home_main"])
    page.wait_for_timeout(1000)
    # 2. 로그인 토큰 주입
    access_token = login_with_token(page,"kakao")
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

# 캘린더 날짜 선택 
def get_reservation_datetime(page: Page):
    now = datetime.now()

    if now.day <= 20:
        target_year = now.year
        target_month = now.month
        start_day = now.day + 1
    else:
        target_month = now.month + 1 if now.month < 12 else 1
        target_year = now.year if now.month < 12 else now.year + 1
        start_day = 1
        page.click('[data-testid="btn_next"]')
        page.wait_for_timeout(300)

    candidate_days = list(range(start_day, 32))
    random.shuffle(candidate_days)

    for day in candidate_days:
        mmdd = f"{target_month:02}{day:02}"
        testid = f"btn_day_{mmdd}"
        span = page.locator(f'[data-testid="{testid}"]')
        button = span.locator("xpath=ancestor::button[1]")

        try:
            if button.get_attribute("disabled") is not None:
                print(f"⛔ 비활성 날짜: {mmdd}")
                continue

            button.click(force=True)
            print(f"✅ 예약일 선택 성공: {mmdd}")
            return {
                "date": f"{target_year}-{target_month:02}-{day:02}",
                "day": day,
                "month": target_month
            }
        except Exception as e:
            print(f"⚠️ 예외 발생({mmdd}): {e}")
            continue

    raise Exception("❌ 모든 날짜가 비활성화되어 예약이 불가능합니다.")

# 예약 정보 생성 (시간 선택 기준)
def get_available_time_button(page: Page):
    time_buttons = page.locator("[data-testid^='btn_time_']")
    count = time_buttons.count()
    print(f"⏱️ 전체 시간 버튼 개수: {count}")

    enabled_buttons = []
    for i in range(count):
        btn = time_buttons.nth(i)
        if btn.get_attribute("disabled") is None:
            enabled_buttons.append(btn)

    if not enabled_buttons:
        raise Exception("❌ 활성화된 시간 버튼이 없습니다.")

    selected_btn = random.choice(enabled_buttons)
    testid = selected_btn.get_attribute("data-testid")
    time_value = testid.split("_")[-1]
    hour, minute = int(time_value[:2]), int(time_value[2:])

    selected_btn.click()
    page.wait_for_timeout(1000)

    print(f"✅ 랜덤 선택된 시간: {hour:02}:{minute:02}")
    return f"{hour:02}:{minute:02}"



# 언어변경 분기 
def switch_language_to_english(page: Page, is_mobile: bool):
    if is_mobile:
        # 1. 모바일 메뉴 오픈
        page.locator('[data-testid="header_menu"]').click()
        page.wait_for_timeout(2000)

        # 2. 영어 선택
        page.locator('[data-testid="language_eng"]').click()
        page.wait_for_timeout(1000)

        # 3. 새로고침
        page.locator('[data-testid="menu_discover"]').click()
        page.wait_for_timeout(1000)
    else:
        # PC에서는 직접 언어 버튼 클릭
        page.locator('[data-testid="drop_language"]').click()
        page.wait_for_timeout(1000)
        page.locator('[data-testid="drop_language_eng"]').click()
        page.wait_for_timeout(1000)
