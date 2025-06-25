from playwright.sync_api import Page, expect
from config import URLS
from helpers.customer_utils import cen_login
from helpers import image_assets as img

def check_invalid_upload(page: Page, file_path: str, toast_testid: str):
    page.set_input_files('[data-testid="upload_image"]', file_path)
    page.wait_for_timeout(500)
    expect(page.locator(f'[data-testid="{toast_testid}"]')).to_be_visible(timeout=3000)
    print(f"✅ {toast_testid} 토스트 확인 완료")
def test_event_validations(page: Page):
    cen_login(page)

    # ✅ [1] 이미지 업로드 유효성 확인
    page.goto(URLS["cen_event"])
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_register_event"]')
    page.wait_for_timeout(1000)

    check_invalid_upload(page, img.overspec_img, "toast_image_size")
    page.wait_for_timeout(1000)
  
    check_invalid_upload(page, img.nonspec_img, "toast_image_format")
    page.wait_for_timeout(1000)
    check_invalid_upload(page, img.nonspec_video, "toast_image_format")
    page.wait_for_timeout(1000)
 
    # # ✅ [2] 미노출 그룹 노출 시도 → toggle 클릭 → 비활성화 토스트
    page.goto(URLS["cen_event"])
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_group"]', "미노출이벤트")
    page.locator("body").click(position={"x": 10, "y": 10})
    page.wait_for_timeout(1000)
    # # 리스트에서 확인
    row = page.locator("table tbody tr").first
    row.locator('[data-testid="toggle_event"]').click()
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_confirm"]')
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_inactive"]')).to_be_visible(timeout=3000)
    print("✅ 미노출 그룹의 토글 비활성화 토스트 확인 완료")
    page.wait_for_timeout(1000)
 
    # 수정화면 진입 후 확인
    row.locator("td").last.click()
    page.wait_for_timeout(1000)
    page.locator('[data-testid="btn_review"]').click()
    page.wait_for_timeout(1000)
    page.locator('[data-testid="btn_edit"]').click()
    page.wait_for_timeout(1000)
    page.locator('[data-testid="btn_show"]').click()
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_complete"]')
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_period"]')).to_be_visible(timeout=3000)
    print("✅ 이벤트 기간 재설정 토스트 확인 완료")
    page.wait_for_timeout(1000)


    # ✅ [3] 그룹명 수정 유효성
    page.goto(URLS["cen_event"])
    page.wait_for_timeout(3000)
    page.fill('[data-testid="input_group"]', "자동화이벤트")
    page.locator("body").click(position={"x": 10, "y": 10})
    page.wait_for_timeout(1000)
    cell = page.locator("table tbody tr").first.locator("td").first
    # 이름 변경 
    original_name = cell.inner_text().strip()
    if original_name == "자동화이벤트":
        new_name = "자동화이벤트수정"
    else:
        new_name = "자동화이벤트"
    # 수정모드
    cell.click()
    page.wait_for_timeout(1000)
    input_box = cell.locator("input").first

    # 공백 입력 후 포커스 아웃
    input_box.fill("")
    page.wait_for_timeout(500)
    page.locator("body").click(position={"x": 10, "y": 10})
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_required"]')).to_be_visible(timeout=3000)
    print("✅ 그룹명 공백 입력 시 toast_required 확인 완료")
    page.wait_for_timeout(1000)
    
    # 중복 이름 입력 후 포커스 아웃
    input_box.fill("미노출이벤트")
    page.wait_for_timeout(500)
    page.locator("body").click(position={"x": 10, "y": 10})
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_duplicate"]')).to_be_visible(timeout=3000)
    print("✅ 그룹명 중복 입력 시 toast_duplicate_option 확인 완료")
    page.wait_for_timeout(1000)

    # 정상 입력 후 포커스 아웃
    input_box.fill(new_name)
    page.wait_for_timeout(500)
    page.locator("body").click(position={"x": 10, "y": 10})
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="toast_edit"]')).to_be_visible(timeout=3000)
    print("✅ 그룹명 수정 확인 완료")

