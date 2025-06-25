from datetime import datetime, timedelta
from playwright.sync_api import Page, expect
from config import URLS
from helpers.customer_utils import cen_login
from helpers.event_utils import select_calendar_date, save_events, verify_event_on_homepage, set_visible_events_to_hidden
from helpers import image_assets as img
from pathlib import Path


def test_register_multiple_korean_pc_events(page: Page, count: int = 100):

    from datetime import datetime
    cen_login(page)
    page.goto(URLS["cen_event"])
    page.wait_for_timeout(1000)

    now = datetime.now().strftime("%m%d_%H%M")
    today = datetime.today()
    start_display = today
    end_display = today + timedelta(days=2)

    event_list = []

    for i in range(count):
        group_name = f"이벤트 생성_{now}_{i+1}"
        display_name = f"이벤트_PC_한국어_{now}_{i+1}"

        page.click('[data-testid="btn_register_event"]')
        page.wait_for_timeout(1000)

        # 그룹 생성
        page.click('[data-testid="drop_group_trigger"]')
        page.wait_for_timeout(1000)
        page.click('[data-testid="drop_group_register"]')
        page.wait_for_timeout(1000)
        page.fill('[data-testid="input_group"]', group_name)
        page.wait_for_timeout(1000)
        page.click('[data-testid="btn_accept"]')
        page.wait_for_timeout(1000)

        # 이벤트 노출명
        page.fill('[data-testid="input_event"]', display_name)
        page.wait_for_timeout(1000)
        # 미노출 설정  
        page.click('[data-testid="btn_hide"]')

        # # 노출 기간 설정
        # select_calendar_date(page, "display_startday", start_display)
        # select_calendar_date(page, "display_endday", end_display)

        # 대표 이미지
        main_upload = page.locator('[data-testid="upload_image"]')
        main_upload.wait_for(state="attached", timeout=5000)
        main_upload.element_handle().set_input_files(img.event_img)
        page.wait_for_timeout(3000)
        expect(page.locator('[data-testid="txt_image"]')).to_have_text("img_event.jpg")

        # 상세 이미지 1개만
        detail_upload = page.locator('[data-testid="upload_image_1"]')
        detail_upload.wait_for(state="attached", timeout=5000)
        detail_upload.element_handle().set_input_files(img.detail_img_1)
        page.wait_for_timeout(3000)
        expect(page.locator('[data-testid="txt_image_1"]')).to_have_text(Path(img.detail_img_1).name)

        # 저장
        page.click('[data-testid="btn_complete"]')
        page.wait_for_timeout(500)
        expect(page.locator('[data-testid="toast_register"]')).to_be_visible()
        page.wait_for_timeout(1000)

        event_list.append({
            "group_name": group_name,
            "event_name": display_name,
            "event_period": "상시 진행중",
            "display_period": f"{start_display.strftime('%Y.%m.%d')}-{end_display.strftime('%Y.%m.%d')}",
            "event_visible": "yes",
            "event_description": "",
            "popup_usage": "no",
            "popup_url": ""
        })

    print(f"{count}개 이벤트 등록 완료")

