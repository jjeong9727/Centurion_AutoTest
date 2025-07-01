from playwright.sync_api import Page, expect



# 수정 이탈 팝업 확인
def check_unsave_popup(page: Page):
    page.click('[data-testid="btn_back"]')
    page.wait_for_timeout(1000)
    expect(page.locator('[data-testid="txt_unsave"]')).to_have_text("변경사항을 저장하지 않으시겠습니까?", timeout=3000)
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_cancel"]')
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_back"]')
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_confirm"]')
    page.wait_for_timeout(1000)