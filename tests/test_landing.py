from playwright.sync_api import Page, expect
from config import URLS
import os

def test_landing_links_and_download(page: Page, tmp_path):
    # 1. 메인 페이지 진입
    page.goto(URLS["home_main"])
    page.wait_for_timeout(3000)

# 2. '예약 문의' 버튼 클릭 → 페이지 이동 확인
    reserve_link = page.get_by_role("link", name="예약 문의")
    reserve_link.scroll_into_view_if_needed()
    expect(reserve_link).to_be_visible()
    page.wait_for_timeout(3000)
    reserve_link.click()
    page.wait_for_timeout(3000)
    expect(page).to_have_url(URLS["home_reservation"])
    page.wait_for_timeout(3000)

    # 3. 뒤로가기
    page.go_back()
    page.wait_for_timeout(5000)

    # 4. 최하단으로 스크롤
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(3000)

    # 5. 인스타그램 버튼 클릭 → 새 탭 이동 확인
    with page.expect_popup() as popup_info:
        page.locator("a[href*='instagram.com']").click()
        page.wait_for_timeout(3000)
    insta_page = popup_info.value
    insta_page.wait_for_load_state()
    page.wait_for_timeout(3000)
    assert "instagram.com" in insta_page.url
    page.wait_for_timeout(3000)
    insta_page.close()
    page.wait_for_timeout(3000)

    # 6. 다시 하단으로 스크롤
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(3000)

    # 7. 개인정보처리방침 클릭 → 이동 확인
    page.get_by_role("link", name="개인정보취급방침").click()
    page.wait_for_timeout(5000)
    expect(page).to_have_url(URLS["home_privacy"])
    page.wait_for_timeout(3000)

    # 8. 뒤로가기
    page.go_back()
    page.wait_for_timeout(3000)

    # 9. 미성년자 시술 동의서 클릭 → 파일 다운로드 확인
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(3000)
    with page.expect_download() as download_info:
        page.get_by_role("link", name="미성년자시술동의서").click()
    page.wait_for_timeout(3000)
    download = download_info.value
    download_path = download.path()
    page.wait_for_timeout(3000)
    assert os.path.exists(download_path), "❌ 파일 다운로드 실패"
