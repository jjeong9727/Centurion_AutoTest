# 녹취시작|일시정지|녹취종료|파일다운로드
# 시작 후 일정 시간 뒤에 종료 > 파일 다운로드 시 정상 다운로드 확인
import os
import pytest
from playwright.sync_api import Page, expect
from config import URLS

DOWNLOAD_DIR = os.path.abspath("downloads")
ALLOWED_EXTENSIONS = [".mp3", ".wav"]  # 필요 시 확장자 추가

@pytest.mark.skip_browser("webkit")
def test_recording_flow_with_cancel(page: Page):
    # 👉 다운로드 폴더 생성
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    page.context.set_default_downloads_path(DOWNLOAD_DIR)

    # 1. URL 진입
    page.goto(URLS["cen_record"])  # 실제 URL로 변경
    page.wait_for_load_state("domcontentloaded")

    # 2. 녹취 시작
    page.click('[data-testid="start"]')
    print("✅ 녹취 시작")
    page.wait_for_timeout(2000)

    # 3. 일시정지
    page.click('[data-testid="pause"]')
    print("⏸️ 일시정지")
    page.wait_for_timeout(1000)
    download_btn = page.locator('[data-testid="download"]')
    expect(download_btn).to_be_visible(timeout=2000)
    assert download_btn.is_disabled(), "❌ 일시정지 후 다운로드 버튼이 비활성화 상태여야 함"
    print("🚫 다운로드 버튼 비활성화 상태 확인 (일시정지 후)")

    # 4. 재개
    page.click('[data-testid="start"]')
    print("▶️ 재개")
    page.wait_for_timeout(2000)

    # 5. 종료
    page.click('[data-testid="stop"]')
    print("⏹️ 녹취 종료")

    # 6. 다운로드 버튼 확인 → 클릭 및 다운로드
    expect(download_btn).to_be_enabled(timeout=3000)
    print("✅ 녹취 종료 후 다운로드 버튼 활성화 확인")


    with page.expect_download() as download_info:
        download_btn.click()
    download = download_info.value
    file_path = download.path()
    file_name = os.path.basename(file_path)
    print(f"✅ 파일 다운로드 완료: {file_name}")

    # 7. 다운로드 파일 존재 및 확장자 확인
    assert os.path.exists(file_path), "❌ 다운로드 파일 없음"
    assert any(file_name.endswith(ext) for ext in ALLOWED_EXTENSIONS), f"❌ 허용되지 않은 파일 형식: {file_name}"

    print("🎧 파일 확장자 검사 통과")

    # 🔁 새 녹음 테스트를 위해 페이지 리로드
    page.reload()
    page.wait_for_timeout(1000)

    # 8. 다시 녹음 시작
    page.click('[data-testid="start"]')
    page.wait_for_timeout(2000)

    # 9. 취소 버튼 클릭 → 녹음 취소
    page.click('[data-testid="cancle"]')
    print("❌ 녹취 취소")

    # 10. 다운로드 버튼이 비활성화 또는 미노출 상태인지 확인
    download_btn_after_cancel = page.locator('[data-testid="download"]')
    try:
        expect(download_btn_after_cancel).not_to_be_visible(timeout=3000)
        print("✅ 취소 후 다운로드 버튼 비노출 확인")
    except AssertionError:
        assert download_btn_after_cancel.is_disabled(), "❌ 취소 후에도 다운로드 버튼이 활성 상태입니다."

