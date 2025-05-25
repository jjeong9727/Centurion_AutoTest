import os
from playwright.sync_api import Page, expect
from config import URLS

def test_landing_links_and_download(page: Page, tmp_path):
    # 1. 메인 페이지 진입
    page.goto(URLS["home_main"])

    # 2. '예약하러 가기' 버튼 클릭 → 페이지 이동 확인
    reserve_button = page.get_by_role("button", name="예약하러 가기")
    reserve_button.scroll_into_view_if_needed()
    expect(reserve_button).to_be_visible()
    reserve_button.click()
    expect(page).to_have_url(URLS["home_reservation"])

    # 3. 뒤로가기
    page.go_back()

    # 4. 최하단으로 스크롤
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    # 5. 인스타그램 버튼 클릭 → 새 탭 이동 확인
    with page.expect_popup() as popup_info:
        page.locator("a[href*='instagram.com']").click()
    insta_page = popup_info.value
    insta_page.wait_for_load_state()
    assert "instagram.com" in insta_page.url
    insta_page.close()

    # 6. 다시 하단으로 스크롤
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    # 7. 개인정보처리방침 클릭 → 이동 확인
    page.get_by_role("link", name="개인정보취급방침").click()
    expect(page).to_have_url(URLS["home_policy"]))

    # 8. 뒤로가기
    page.go_back()

    # 9. 미성년자 시술 동의서 클릭 → 파일 다운로드 확인
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    with page.expect_download() as download_info:
        page.get_by_role("link", name="미성년자시술동의서").click()
    download = download_info.value
    download_path = download.path()
    assert os.path.exists(download_path), "❌ 파일 다운로드 실패"
