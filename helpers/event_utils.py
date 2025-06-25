import json
from typing import Dict, Any
from playwright.sync_api import Page
from datetime import datetime, timedelta
from playwright.sync_api import Page, expect
from datetime import datetime
from typing import Dict
from config import URLS
from urllib.parse import urljoin

EVENT_FILE_PATH = "data/event.json"

# 그룹명 기준으로 json에서 이벤트 불러오기
def get_events_by_group(group_name: str) -> list[Dict[str, Any]]:
    """그룹명 기준으로 이벤트 목록 필터링"""
    try:
        with open(EVENT_FILE_PATH, "r", encoding="utf-8") as f:
            events = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        events = []

    filtered = [event for event in events if event.get("group_name") == group_name]
    print(f"🔍 그룹명 '{group_name}' 기준으로 {len(filtered)}개 이벤트 불러옴")
    return filtered


# 이벤트 정보 json에 저장
def save_events(events: list[Dict[str, Any]]) -> None:
    with open(EVENT_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

# 이벤트 수정 후 json 업데이트
def update_event_field(event_name: str, field: str, new_value: str) -> bool:
    """이벤트 이름 기준으로 특정 필드 업데이트"""
    try:
        with open(EVENT_FILE_PATH, "r", encoding="utf-8") as f:
            events = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        events = []

    updated = False
    for event in events:
        if event.get("event_name") == event_name:
            if field in event:
                event[field] = new_value
                updated = True
                break

    if updated:
        save_events(events)
        print(f"🔄 '{event_name}'의 '{field}' 필드가 '{new_value}'(으)로 업데이트 되었습니다.")
    else:
        print(f"⚠️ '{event_name}' 이벤트 또는 필드 '{field}'를 찾을 수 없습니다.")

    return updated

# 존재하는 모든 이벤트 미노출로 변경
def set_visible_events_to_hidden(page: Page):
    # 1. "노출" 상태 필터 선택
    page.click('[data-testid="drop_status_trigger"]')
    page.wait_for_timeout(1000)
    page.click('[data-value="노출"]')
    page.wait_for_timeout(1000)

    count = 0
    while True:
        # 2. 현재 첫 번째 노출 이벤트 토글 선택
        toggle = page.locator('[data-testid="toggle_event"][data-state="checked"]').first
        if not toggle.is_visible():
            break  # 더 이상 노출 상태 이벤트가 없으면 종료

        # 3. 토글 클릭 → 미노출로 전환
        toggle.scroll_into_view_if_needed()
        toggle.click()
        page.wait_for_timeout(1000)

        page.click('[data-testid="btn_confirm"]')
        page.wait_for_timeout(500)

        # 4. 토스트 확인
        expect(page.locator('[data-testid="toast_status"]')).to_be_visible(timeout=3000)
        page.wait_for_timeout(1000)

        count += 1

    print(f"✅ {count}개 항목 미노출 처리 완료")


# 이벤트 날짜 선택 
def select_calendar_date(page: Page, testid: str, target_date: datetime):
    page.click(f'[data-testid="{testid}"]')
    page.wait_for_timeout(1000)

    # 현재 달과 목표 달이 다르면 달 이동 (예: 다음달 버튼 클릭)
    current = datetime.today()
    if current.month != target_date.month:
        page.click('[data-testid="btn_next"]')
        page.wait_for_timeout(1000)

    day_str = target_date.strftime("%m%d")  # 예: 06월 19일 → 0619
    page.click(f'[data-testid="btn_day_{day_str}"]')
    page.wait_for_timeout(1000)

def get_popup_url(is_mobile: bool, is_english: bool) -> str:
    base_url = URLS["home_main"]
    lang = "en" if is_english else "ko"
    path = f"/{lang}/m/removal" if is_mobile else f"/{lang}/removal"
    return urljoin(base_url, path)

def get_event_list_url(is_mobile: bool, is_english: bool) -> str:
    base_url = URLS["home_main"].rstrip("/")  
    lang = "en" if is_english else "ko"
    device = "/m" if is_mobile else ""
    return f"{base_url}/{lang}{device}/events"


# ✅ 이벤트 홈페이지 노출 확인 함수
def verify_event_on_homepage(page: Page, event: Dict[str, str], is_mobile: bool, is_english: bool):


    # ✅ 이벤트 리스트 화면으로 이동 
    event_url = get_event_list_url(is_mobile, is_english)
    page.goto(event_url)
    page.wait_for_timeout(3000)

    # ✅ 이벤트 노출 여부 확인
    visible_on_list = False
    items = page.locator('[data-testid="txt_event_title"]')
    count = items.count()

    visible_on_list = False

    for i in range(count):
        title_el = items.nth(i)
        title = title_el.inner_text().strip()

        print(f"🔍 비교중: 화면='{title}', JSON='{event['event_name']}'")

        if title == event["event_name"]:
            # ✅ 타이틀 기준으로 상위 div에서 기간, 버튼 탐색
            wrapper = title_el.locator("xpath=../../..")  # 타이틀에서 3단계 상위로 올라감 (div.flex.w-full.flex-col → div.flex.w-full.flex-col → div.flex-col)

            period = wrapper.locator('[data-testid="txt_event_period"]').inner_text().strip()
            print(f"📆 화면 기간='{period}', JSON 기간='{event['event_period']}'")

            if period == event["event_period"]:
                visible_on_list = True
                # ✅ 상세 보기 진입
                wrapper.locator('[data-testid="btn_event"]').click()
                page.wait_for_timeout(1000)
                break

    assert visible_on_list, f"❌ 리스트에 '{event['event_name']}' 노출되지 않음"


    # ✅ 상세 정보 확인
    title_expected = "Ceramique Event" if is_english else "세라미크 이벤트"
    expect(page.locator('[data-testid="txt_title"]')).to_contain_text(title_expected)
    expect(page.locator('[data-testid="txt_event_title"]')).to_have_text(event["event_name"])
    expect(page.locator('[data-testid="txt_event_description"]')).not_to_be_empty()

    print(f"✅ '{event['event_name']}' 노출 확인 완료")

    # 예약 하러 가기 버튼 동작 확인
    page.wait_for_timeout(1000)
    page.click(f'[data-testid="btn_reservation"]')
    page.wait_for_timeout(3000)
    expect(page.locator('[data-testid="txt_login"]')).to_be_visible(timeout=3000)
    print("✅ 예약하러가기 버튼 동작 확인 완료")

 
    # ✅ 팝업 확인
    popup_url = get_popup_url(is_mobile, is_english)
    page.goto(popup_url)
    page.wait_for_timeout(1000)

    popup_locator = page.locator('[data-testid="event_popup"]')
    popup_visible = popup_locator.is_visible()
    expected_popup = event["popup_usage"] == "yes"
    assert popup_visible == expected_popup, (
        f"❌ 팝업 노출 여부 오류: {popup_visible} (예상: {expected_popup})"
    )


    # ✅ 팝업 클릭 시 이동 URL 확인
    if popup_visible:
        popup_url_type = event["popup_url"]

        popup_locator.click()
        page.wait_for_load_state()
        actual_url = page.url

        if popup_url_type == "event":
            assert "/events" in actual_url, (
                f"❌ 팝업 클릭 후 URL 오류: {actual_url} (예상 포함: '/events')"
            )
        elif popup_url_type == "instagram":
            assert "instagram.com" in actual_url, (
                f"❌ Instagram URL 이동 실패: {actual_url}"
            )


