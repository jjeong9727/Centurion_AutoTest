from playwright.sync_api import Page, expect
from config import URLS, is_mobile
import os

def test_landing_links_and_download(page: Page, tmp_path):
    # 1. 메인 페이지 진입
    page.goto(URLS["home_main"])
    page.wait_for_timeout(1000)

    # 2. '예약 문의' 또는 '예약' 버튼 클릭 → 페이지 이동 확인
    button_name = "예약" if is_mobile else "예약 문의"
    reserve_link = page.get_by_text(button_name, exact=True)
    reserve_link.scroll_into_view_if_needed()
    expect(reserve_link).to_be_visible()
    reserve_link.click()

    page.wait_for_timeout(2000)
    expect(page).to_have_url(URLS["home_reservation"])
    page.wait_for_timeout(2000)

    # 3. 뒤로가기
    page.go_back()
    page.wait_for_timeout(3000)

    # 4. 최하단으로 스크롤
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(2000)

    # 5. 인스타그램 버튼 클릭 → 새 탭 이동 확인 및 주소 검증
    with page.expect_popup() as popup_info:
        page.locator("a[href*='instagram.com']").click()
        page.wait_for_timeout(2000)

    insta_page = popup_info.value
    insta_page.wait_for_load_state()
    page.wait_for_timeout(2000)

    # ✅ 인스타그램 주소 시작 확인
    assert insta_page.url.startswith("https://www.instagram.com/"), \
        f"❌ 인스타그램 주소가 예상과 다릅니다: {insta_page.url}"

    insta_page.close()
    page.wait_for_timeout(2000)


    # 6. 다시 하단으로 스크롤
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(2000)

    # 7. 개인정보처리방침 클릭 → 이동 확인
    page.get_by_role("link", name="개인정보취급방침").click()
    page.wait_for_timeout(3000)
    expect(page).to_have_url(URLS["home_privacy"])
    page.wait_for_timeout(2000)

    # 8. 뒤로가기
    page.go_back()
    page.wait_for_timeout(2000)

    # 9. 미성년자 시술 동의서 클릭 → 파일 다운로드 확인
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(2000)
    with page.expect_download() as download_info:
        page.get_by_role("link", name="미성년자시술동의서").click()
    page.wait_for_timeout(2000)
    download = download_info.value
    download_path = download.path()
    page.wait_for_timeout(2000)
    assert os.path.exists(download_path), "❌ 파일 다운로드 실패"
