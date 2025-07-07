import json
from pathlib import Path
from typing import List, Dict
from playwright.sync_api import Page

from helpers.event_utils import verify_event_on_homepage  # 이미 구현한 함수 사용

EVENT_JSON_PATH = Path("data/event.json")

def load_saved_events() -> List[Dict[str, str]]:
    with open(EVENT_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def test_verify_registered_events(page: Page):
    events = load_saved_events()

    for event in events:
        event_name = event.get("event_name", "")
        
        is_mobile = "모바일" in event_name
        is_english = "영어" in event_name

        print(f"🔍 event: {event_name}, is_mobile: {is_mobile}, is_english: {is_english}")

        verify_event_on_homepage(
            page,
            event,
            is_mobile=is_mobile,
            is_english=is_english
        )
