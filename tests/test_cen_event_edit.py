import json
import random
from datetime import datetime, timedelta
from playwright.sync_api import Page, expect
from config import URLS
from helpers.customer_utils import cen_login
from helpers.event_utils import select_calendar_date, verify_event_on_homepage
from helpers import image_assets as img

EVENT_FILE = "data/event.json"

def load_events():
    with open(EVENT_FILE, encoding="utf-8") as f:
        return json.load(f)

def update_event_json(data: list):
    with open(EVENT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def test_edit_event(page: Page):
    events = load_events()
    assert events, "❌ 수정할 이벤트 데이터가 없습니다."

    cen_login(page)

    for idx, event in enumerate(events):
        page.goto(URLS["cen_event"])
        page.wait_for_timeout(1000)

        # ✅ 그룹명 검색 후 수정 화면 진입
        page.fill('[data-testid="input_group"]', event["group_name"])
        page.locator("body").click(position={"x": 10, "y": 10})
        page.wait_for_timeout(1000)

        row = page.locator("table tbody tr").first
        row.locator("td").last.click()
        page.wait_for_timeout(1000)
        page.locator('[data-testid="btn_review"]').click()  # 상세 진입
        page.wait_for_timeout(1000)

        # ✅ 유형 선택 - 브라우저/언어
        is_mobile = "모바일" in event["event_name"]
        is_english = "영어" in event["event_name"]

        if is_mobile:
            page.click('[data-testid="drop_browser"]')
            page.wait_for_timeout(1000)
            page.get_by_role("option", name="모바일").click()
        if is_english:
            page.click('[data-testid="drop_language"]')
            page.wait_for_timeout(1000)
            page.get_by_role("option", name="영어").click()
        page.wait_for_timeout(1000)

        page.locator('[data-testid="btn_edit"]').click()  # 수정 모드 변경
        page.wait_for_timeout(1000)

        # ✅ 이벤트 노출명 수정 
        new_event_name = f"수정_{event['event_name']}"
        page.fill('[data-testid="input_event"]', new_event_name)
        page.wait_for_timeout(1000)

        # ✅ 대표 이미지 수정
        upload_locator = page.locator('[data-testid="upload_image"]')
        upload_locator.wait_for(state="attached", timeout=5000)
        element = upload_locator.element_handle()
        assert element is not None, "❌ 파일 업로드 input 요소를 찾을 수 없습니다."
        element.set_input_files(img.edit_img)
        page.wait_for_timeout(5000)
        expect(page.locator('[data-testid="txt_image"]')).to_have_text("img_edit_event.png")

        # ✅ 상세 이미지 중 하나만 교체 (1번 이미지 고정)
        random_idx = random.randint(1, 6)

        upload_locator = page.locator(f'[data-testid="upload_image_{random_idx}"]')
        upload_locator.wait_for(state="attached", timeout=5000)

        element = upload_locator.element_handle()
        assert element is not None, f"❌ 상세 이미지 {random_idx}번 input 요소를 찾을 수 없습니다."

        element.set_input_files(img.edit_detail)

        page.wait_for_timeout(5000)

        expect(page.locator(f'[data-testid="txt_image_{random_idx}"]')).to_have_text("img_edit_detail.png")
        page.wait_for_timeout(1000)


        # ✅ 이벤트 노출 기간 수정 (한국어만)
        if "한국어" in event["event_name"]:
            tomorrow = datetime.today() + timedelta(days=1)
            select_calendar_date(page, "display_startday", tomorrow)
            page.wait_for_timeout(1000)
            start_display = tomorrow.strftime("%Y.%m.%d")
            end_display = event["display_period"].split("-")[1]
        else:
            start_display = event["display_period"].split("-")[0]
            end_display = event["display_period"].split("-")[1]

        # ✅ 팝업 사용 여부 반전
        original = event["popup_usage"]
        if original == "yes":
            page.click('[data-testid="toggle_use"]')
            new_popup = "no"
        else:
            page.click('[data-testid="toggle_use"]')
            new_popup = "yes"

        # ✅ 팝업 이미지 수정
        page.set_input_files('[data-testid="upload_popup"]', img.edit_popup)
        page.wait_for_timeout(5000)
        expect(page.locator('[data-testid="txt_popup_image"]')).to_have_text("img_edit_popup.jpg")
        page.wait_for_timeout(1000)

        # ✅ 팝업 URL 수정
        page.fill('[data-testid="input_popup_link"]', URLS["footer_instagram"])
        page.wait_for_timeout(1000)

        # ✅ 완료 저장
        page.click('[data-testid="btn_complete"]')
        page.wait_for_timeout(500)
        expect(page.locator('[data-testid="toast_edit"]')).to_be_visible()
        page.wait_for_timeout(1000)

        # ✅ 홈페이지 반영 확인
        event["event_name"] = new_event_name
        event["display_period"] = f"{start_display}-{end_display}"
        event["popup_usage"] = new_popup
        event["popup_url"] = "instagram"

        is_mobile = "모바일" in new_event_name
        is_english = "영어" in new_event_name

        try:
            verify_event_on_homepage(
                page,
                event,
                is_mobile=is_mobile,
                is_english=is_english
            )
        except AssertionError as e:
            print(f"❌ 홈페이지 노출 확인 실패: {new_event_name} - {e}")


    update_event_json(events)
    print("✅ 이벤트 수정 및 JSON 업데이트 완료")
