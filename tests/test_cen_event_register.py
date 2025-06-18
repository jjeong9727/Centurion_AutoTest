
from datetime import datetime, timedelta
from playwright.sync_api import Page
from helpers.event_utils import select_calendar_date
from config import URLS
from helpers.customer_utils import cen_login

def register_event_text_info(page: Page, group_name: str, is_mobile: bool, is_english: bool):
    # ✅ 유형 선택 - 브라우저
    device = "모바일" if is_mobile else "PC"
    page.click('[data-testid="drop_browser"]')
    page.click(f'text="{device}"')

    # ✅ 유형 선택 - 언어
    language = "영어" if is_english else "한국어"
    page.click('[data-testid="drop_language"]')
    page.click(f'text="{language}"')

    page.wait_for_timeout(500)

    # ✅ 이벤트 그룹 선택
    page.click('[data-testid="drop_group_trigger"]')
    page.fill('[data-testid="drop_group_search"]', group_name)
    page.wait_for_timeout(300)
    page.click('[data-testid="drop_group_item"]')

    # ✅ 이벤트 노출명 입력
    page.fill('[data-testid="input_event"]', group_name)

    # ✅ 날짜 계산
    today = datetime.today()
    start_event = today if not is_english else today + timedelta(days=1)
    end_event = start_event + timedelta(days=10)
    start_display = today if not is_english else today + timedelta(days=1)
    end_display = start_display + timedelta(days=1)

    # ✅ 이벤트 기간 설정
    select_calendar_date(page, "event_startday", start_event)
    select_calendar_date(page, "event_endday", end_event)

    # ✅ 노출 기간 설정
    select_calendar_date(page, "display_startday", start_display)
    select_calendar_date(page, "display_endday", end_display)

    print(f"✅ 텍스트 등록 완료: {device} / {language}")

def test_register_event_text_only(page: Page):
    cen_login(page)
    page.goto(URLS["cen_event"])
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_register_event"]')
    page.wait_for_timeout(1000)

    group_name = "여름이벤트"

    # PC/모바일 × 한국어/영어
    for is_mobile, is_english in [
        (False, False),  # PC 한국어
        (True, False),   # Mobile 한국어
        (False, True),   # PC 영어
        (True, True),    # Mobile 영어
    ]:
        register_event_text_info(page, group_name, is_mobile, is_english)

    # 완료 버튼 클릭까지 추가하려면 아래 주석 해제
    # page.click('[data-testid="btn_complete"]')
    # page.wait_for_selector('[data-testid="toast_register"]')
