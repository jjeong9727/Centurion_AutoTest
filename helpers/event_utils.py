import json
from typing import Dict, Any
from playwright.sync_api import Page
from datetime import datetime, timedelta

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

def select_calendar_date(page: Page, testid: str, date: datetime):
    """날짜 캘린더 열고 날짜 선택"""
    page.click(f'[data-testid="{testid}"]')
    mmdd = date.strftime("%m%d")
    page.click(f'[data-testid="btn_day_{mmdd}"]')
    page.wait_for_timeout(300)