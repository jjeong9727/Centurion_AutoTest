from datetime import datetime, timedelta
from playwright.sync_api import Page, expect
from config import URLS
from helpers.customer_utils import cen_login
from helpers.event_utils import select_calendar_date, save_events, verify_event_on_homepage, set_visible_events_to_hidden
from helpers import image_assets as img
from pathlib import Path
def generate_display_name(mobile: bool, english: bool, now: str) -> str:
    device = "모바일" if mobile else "PC"
    lang = "영어" if english else "한국어"
    return f"이벤트_{device}_{lang}_{now}"
def fill_event_form(
    page: Page,
    group_name: str,
    display_name: str,
    is_mobile: bool,
    is_english: bool,
    first_register: bool,
    last_register: bool,
    idx : int,
    popup_url: str = ""
) -> dict:
    page.click('[data-testid="btn_register_event"]')
    page.wait_for_timeout(1000)
    # ✅ 유형 선택 - 브라우저/언어 (기본이 PC/한국어면 생략)
    if not first_register:
        if is_mobile:
            page.click('[data-testid="drop_browser"]')
            page.wait_for_timeout(1000)
            page.get_by_role("option", name="모바일").click()
        if is_english:
            page.click('[data-testid="drop_language"]')
            page.wait_for_timeout(1000)
            page.get_by_role("option", name="영어").click()
        page.wait_for_timeout(1000)

    # ✅ 이벤트 그룹
    page.click('[data-testid="drop_group_trigger"]')
    page.wait_for_timeout(1000)
    if first_register:
        # 그룹 추가
        page.click('[data-testid="drop_group_register"]')
        page.wait_for_timeout(1000)
        page.fill('[data-testid="input_group"]', group_name)
        page.wait_for_timeout(1000)
        page.click('[data-testid="btn_accept"]')
        page.wait_for_timeout(1000)
    else:
        # 기존 그룹 선택
        page.fill('[data-testid="drop_group_search"]', group_name)
        page.wait_for_timeout(1000)
        page.locator(f'[data-testid="drop_group_item"]:has-text("{group_name}")').first.click()
        page.wait_for_timeout(1000)

    # ✅ 이벤트 노출명 입력
    page.fill('[data-testid="input_event"]', display_name)
    page.wait_for_timeout(1000)


    # ✅ 기간 설정
    today = datetime.today()
    start_event = None
    end_event = None

    if idx == 0:
        # 상시 진행중: 시작일/종료일 없음
        pass
    elif idx == 1:
        end_event = today + timedelta(days=30)
    elif idx == 2:
        start_event = today
    elif idx == 3:
        start_event = today
        end_event = today + timedelta(days=30)

    if start_event:
        select_calendar_date(page, "event_startday", start_event)
    if end_event:
        select_calendar_date(page, "event_endday", end_event)

    # 노출 기간은 고정
    start_display = today
    end_display = today + timedelta(days=2)
    select_calendar_date(page, "display_startday", start_display)
    select_calendar_date(page, "display_endday", end_display)

    # ✅ 기간 정보 포맷 저장용 문자열 구성
    if not start_event and not end_event:
        event_period = "상시 진행중"
    elif not start_event and end_event:
        event_period = f"-{end_event.strftime('%Y.%m.%d')}"
    elif start_event and not end_event:
        event_period = f"{start_event.strftime('%Y.%m.%d')}-미정"
    else:
        event_period = f"{start_event.strftime('%Y.%m.%d')}-{end_event.strftime('%Y.%m.%d')}"

    # ✅ 이미지 업로드
    upload_locator = page.locator('[data-testid="upload_image"]')
    upload_locator.wait_for(state="attached", timeout=5000)
    element = upload_locator.element_handle()
    assert element is not None, "❌ 파일 업로드 input 요소를 찾을 수 없습니다."
    element.set_input_files(img.event_img)
    page.wait_for_timeout(5000)
    expect(page.locator('[data-testid="txt_image"]')).to_have_text("img_event.jpg")

    # ✅ 상세 이미지 반복 업로드
    for i in range(1, 7):
        image_path = getattr(img, f"detail_img_{i}")
        locator = page.locator(f'[data-testid="upload_image_{i}"]')
        locator.wait_for(state="attached", timeout=5000)

        detail_element = locator.element_handle()
        assert detail_element is not None, f"❌ 상세 이미지 {i}번 input 요소를 찾을 수 없습니다."

        detail_element.set_input_files(image_path)

        page.wait_for_timeout(3000)
        expect(page.locator(f'[data-testid="txt_image_{i}"]')).to_have_text(Path(image_path).name)
        page.wait_for_timeout(1000)


    # ✅ 상세 설명
    description = "여름맞이 피부 리프레시 이벤트! \n 지금 예약 시 최대 30% 할인✨ 모공, 잡티, 탄력까지 한번에 개선하는 프리미엄 케어. 상담 후 맞춤 시술 제안드립니다. 기간: 2025.07.01 ~ 2025.07.31 ☎ 문의: 02-123-4567 \n ※ 시술 전후 주의사항 및 부작용 설명을 꼭 확인해주세요. #여름이벤트 #피부관리"
    page.fill('[data-testid="input_description"]', description)
    page.wait_for_timeout(1000)

    # ✅ 마지막 등록 시: 중복 확인 유도 (유형 고의 중복 → 재설정)
    if last_register:
        # 현재 상태는 PC/한국어 → 등록 시도 → 중복 발생
        page.click('[data-testid="btn_complete"]')
        page.wait_for_timeout(500)
        expect(page.locator('[data-testid="toast_duplicate_option"]')).to_be_visible(timeout=3000)
        page.wait_for_timeout(1000)

        # 다시 모바일/영어로 유형 변경
        page.click('[data-testid="drop_browser"]')
        page.wait_for_timeout(1000)
        page.get_by_role("option", name="모바일").click()
        page.wait_for_timeout(1000)
        page.click('[data-testid="drop_language"]')
        page.wait_for_timeout(1000)
        page.get_by_role("option", name="영어").click()
        page.wait_for_timeout(1000)

        # ✅ 팝업 설정
    if not is_english:
        page.click('[data-testid="toggle_use"]')  # 한국어일 때만 ON
        page.wait_for_timeout(1000)
        # 이미지 없이 팝업 ON → 등록 시도 → 토스트 확인 
        page.click('[data-testid="btn_complete"]')
        page.wait_for_timeout(500)
        expect(page.locator('[data-testid="toast_image_empty"]')).to_be_visible()
        page.wait_for_timeout(1000)

    # 팝업 이미지 업로드
    upload_locator = page.locator('[data-testid="upload_popup"]')
    upload_locator.wait_for(state="attached", timeout=5000)

    element = upload_locator.element_handle()
    assert element is not None, "❌ 파일 업로드 input 요소를 찾을 수 없습니다."

    element.set_input_files(img.popup_img)

    page.wait_for_timeout(5000)
    expect(page.locator('[data-testid="txt_popup_image"]')).to_have_text("img_popup.jpg")
    # ✅ 최종 저장
    page.click('[data-testid="btn_complete"]')
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_register"]')).to_be_visible()
    page.wait_for_timeout(1000)

    return {
        "group_name": group_name,
        "event_name": display_name,
        "event_period": event_period,
        "display_period": f"{start_display.strftime('%Y.%m.%d')}-{end_display.strftime('%Y.%m.%d')}",
        "event_visible": "yes",
        "event_description": description,
        "popup_usage": "no" if is_english else "yes",
        "popup_url": "event"
    }

def test_register_event(page: Page):
    cen_login(page)
    page.goto(URLS["cen_event"])
    page.wait_for_timeout(1000)
    

    # # 노출 중인 이벤트 미노출로 모두 변경
    # 🚫 이벤트 기간 경과 시 미노출로 전환 이슈 해결 후 확인 필요  CEN-490
    # set_visible_events_to_hidden(page)

    now = datetime.now().strftime("%m%d_%H%M")
    group_name = f"자동화그룹_{now}"

    options = [
        {"ui": (False, False), "label": (False, False)},  # PC + 한국어
        {"ui": (True, False),  "label": (True, False)},   # 모바일 + 한국어
        {"ui": (False, True),  "label": (False, True)},   # PC + 영어
        {"ui": (False, False), "label": (True, True)}     # UI는 PC+한글, Label은 모바일+영어
         
    ]
        
    event_list = []

    for idx, opt in enumerate(options):
        ui_mobile, ui_english = opt["ui"]
        label_mobile, label_english = opt["label"]
        display_name = generate_display_name(label_mobile, label_english, now)

        event_data = fill_event_form(
            page,
            group_name=group_name,
            display_name=display_name,
            is_mobile=ui_mobile,
            is_english=ui_english,
            first_register=(idx == 0),
            last_register=(idx == 3),
            idx=idx,
            popup_url = "event"
        )
        event_list.append(event_data)


    save_events(event_list)

    
    # ✅ 이벤트 등록 후 홈페이지 노출 확인
    for idx, event in enumerate(event_list):
        event_name = event.get("event_name", "")
        is_mobile = "모바일" in event_name
        is_english = "영어" in event_name

        verify_event_on_homepage(
            page,
            event,
            is_mobile=is_mobile,
            is_english=is_english
        )