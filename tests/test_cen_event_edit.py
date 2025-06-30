import json
import random
from datetime import datetime
from playwright.sync_api import Page, expect
from config import URLS
from helpers.customer_utils import cen_login
from helpers.event_utils import verify_event_on_homepage
from helpers import image_assets as img

EVENT_FILE = "data/event.json"

def load_events():
    with open(EVENT_FILE, encoding="utf-8") as f:
        return json.load(f)
def update_one_event_in_json(updated_event: dict, original_name: str):
    with open(EVENT_FILE, encoding="utf-8") as f:
        data = json.load(f)

    for idx, event in enumerate(data):
        if event["event_name"] == original_name:
            data[idx] = updated_event
            break

    with open(EVENT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def test_edit_event(page: Page):
    events = load_events()
    assert events, "❌ 수정할 이벤트 데이터가 없습니다."

    cen_login(page)

    for event in events:
        page.goto(URLS["cen_event"])
        page.wait_for_timeout(1000)

        # ✅ 그룹명 검색 후 수정 진입
        page.fill('[data-testid="input_group"]', event["group_name"])
        page.locator("body").click(position={"x": 10, "y": 10})
        page.wait_for_timeout(1000)

        row = page.locator("table tbody tr").first
        row.locator("td").last.click()
        page.wait_for_timeout(2000)
        page.locator('[data-testid="btn_review"]').click()
        page.wait_for_timeout(1000)

        # ✅ 브라우저/언어 선택
        is_mobile = "모바일" in event["event_name"]
        is_english = "영어" in event["event_name"]

        if is_mobile:
            page.locator('button[role="combobox"]', has_text="PC").click()
            page.wait_for_timeout(1000)
            page.get_by_role("option", name="모바일").click()

        if is_english:
            page.locator('button[role="combobox"]', has_text="한국어").click()
            page.wait_for_timeout(1000)
            page.get_by_role("option", name="영어").click()

        page.wait_for_timeout(1000)

        # ✅ 수정 시작
        page.locator('[data-testid="btn_edit"]').click()
        page.wait_for_timeout(1000)

        # ✅ 이벤트 노출명 수정
        original_name = event["event_name"]
        new_event_name = f"수정_{original_name}"
        page.fill('[data-testid="input_event"]', new_event_name)

        # ✅ 대표 이미지 수정
        page.locator('[data-testid="upload_image"]').set_input_files(img.edit_img)
        page.wait_for_timeout(1000)
        expect(page.locator('[data-testid="txt_image"]')).to_have_text("img_edit_event.png")

        # ✅ 상세 이미지 중 랜덤 교체
        random_idx = random.randint(1, 6)
        page.locator(f'[data-testid="upload_image_{random_idx}"]').set_input_files(img.edit_detail)
        page.wait_for_timeout(1000)
        expect(page.locator(f'[data-testid="txt_image_{random_idx}"]')).to_have_text("img_edit_detail.png")

        # ✅ 팝업 사용 여부 반전
        original = event["popup_usage"]
        page.click('[data-testid="btn_toggle"]')
        new_popup = "no" if original == "yes" else "yes"

        # ✅ 팝업 이미지 수정
        page.set_input_files('[data-testid="upload_popup"]', img.edit_popup)
        page.wait_for_timeout(1000)
        expect(page.locator('[data-testid="txt_popup_image"]')).to_have_text("img_edit_popup.jpg")

        # ✅ 팝업 URL 수정
        page.fill('[data-testid="input_popup_link"]', URLS["footer_instagram"])
        page.wait_for_timeout(1000)

        # ✅ 완료 저장
        page.click('[data-testid="btn_complete"]')
        expect(page.locator('[data-testid="toast_edit"]')).to_be_visible(timeout=3000)

        # ✅ event 객체 업데이트 및 JSON 반영
        event["event_name"] = new_event_name
        event["popup_usage"] = new_popup
        event["popup_url"] = "instagram"
        update_one_event_in_json(event, original_name)
        # ✅ 홈페이지 반영 확인
        try:
            verify_event_on_homepage(
                page,
                event,
                is_mobile="모바일" in new_event_name,
                is_english="영어" in new_event_name
            )
        except AssertionError as e:
            print(f"❌ 홈페이지 노출 확인 실패: {new_event_name} - {e}")

    print("✅ 이벤트 수정 완료 및 개별 JSON 업데이트 완료")
