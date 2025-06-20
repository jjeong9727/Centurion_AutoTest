import json
from typing import Dict, Any
from playwright.sync_api import Page
from datetime import datetime, timedelta
from playwright.sync_api import Page, expect
from datetime import datetime
from typing import Dict
from config import URLS

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
    # 1. 상태 드롭다운 열기 및 "노출" 필터 선택
    page.click('[data-testid="drop_status"]')
    page.wait_for_timeout(1000)
    page.click('text=노출') 
    page.wait_for_timeout(1000)

    page_index = 1
    while True:
        print(f"📄 {page_index} 페이지 처리 중...")

        # 2. 현재 페이지에서 data-state="checked" 토글 모두 선택
        toggles = page.locator('[data-testid="toggle_event"][data-state="checked"]')
        count = toggles.count()

        for i in range(count):
            toggle = toggles.nth(i)
            toggle.scroll_into_view_if_needed()
            toggle.click()
            page.wait_for_timeout(1000)  # 토글 후 약간의 대기
            page.click('[data-testid="btn_accept"]')
            page.wait_for_timeout(500)
            expect(page.locator('[data-testid="toast_status"]')).to_be_visible(timeout=3000)
            page.wait_for_timeout(1000)

        print(f"✅ {count}개 항목 미노출 처리 완료")

        # 3. 다음 페이지 존재 여부 확인
        next_button = page.locator('[data-testid="next_page"]')
        is_disabled = next_button.get_attribute("disabled") is not None

        if is_disabled:
            print("✅ 마지막 페이지까지 완료")
            break

        # 4. 다음 페이지로 이동
        next_button.click()
        page.wait_for_timeout(1500)
        page_index += 1

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
    return base_url + path

# ✅ 이벤트 홈페이지 노출 확인 함수
def verify_event_on_homepage(page: Page, event: Dict[str, str], is_mobile: bool, is_english: bool):
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

    # ✅ 팝업 클릭 시 이동할 URL 확인 (노출 시에만 실행)
    if popup_visible:
        with page.expect_popup() as popup_info:
            popup_locator.click()

        new_page = popup_info.value
        new_page.wait_for_load_state()

        expected_url = URLS["home_event"] if event["popup_url"] == "event" else URLS["footer_instagram"]
        actual_url = new_page.url

        assert actual_url.startswith(expected_url), (
            f"❌ 팝업 클릭 후 URL 이동 오류: {actual_url} (예상 시작: {expected_url})"
        )
        print(f"✅ 팝업 URL 이동 확인 완료: {actual_url}")


    # ✅ 이벤트 리스트 화면으로 이동 
    page.goto(URLS["home_event"])
    page.wait_for_timeout(1000)

    # ✅ 이벤트 노출 여부 확인
    visible_on_list = False
    items = page.locator('[data-testid="txt_event_title"]')
    count = items.count()

    for i in range(count):
        title = items.nth(i).inner_text().strip()
        if title == event["event_name"]:
            period = page.locator('[data-testid="txt_event_period"]').nth(i).inner_text().strip()
            if period == event["event_period"]:
                visible_on_list = True
                # ✅ 상세 보기 진입
                page.locator('[data-testid="btn_event"]').nth(i).click()
                page.wait_for_timeout(1000)
                break

    assert visible_on_list, f"❌ 리스트에 '{event['event_name']}' 노출되지 않음"

    # ✅ 상세 정보 확인
    expect(page.locator('[data-testid="txt_title"]')).to_contain_text("세라미크 이벤트")
    expect(page.locator('[data-testid="txt_event_title"]')).to_have_text(event["event_name"])
    expect(page.locator('[data-testid="txt_event_description"]')).not_to_be_empty()

    print(f"✅ '{event['event_name']}' 노출 확인 완료")
