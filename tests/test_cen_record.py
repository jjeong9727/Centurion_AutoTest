# 녹취시작|일시정지|녹취종료|파일다운로드
# 시작 후 일정 시간 뒤에 종료 > 파일 다운로드 시 정상 다운로드 확인
import os
from datetime import datetime
from pathlib import Path
import pytest
from playwright.sync_api import Page, expect, sync_playwright
from config import URLS
from helpers.customer_utils import cen_login

ALLOWED_EXTENSIONS = [".webm"]  # 결정된 확장자

@pytest.mark.skip_browser("webkit")
def test_recording_flow_with_cancel(page: Page):
   
    # try:
        # ✅ 로그인 및 URL 진입
        cen_login(page)
        page.goto(URLS["cen_record"])
        page.wait_for_timeout(2000)

        # ✅ 녹취 시작 시간 저장
        start_time = datetime.now()
        formatted_start_time = start_time.strftime("%Y%m%d_%H%M%S")

        # ✅ 녹취 시작
        page.click('[data-testid="start"]')
        print(f"✅ 녹취 시작 ({formatted_start_time})")
        page.wait_for_timeout(10000)

        # ✅ 일시정지
        page.click('[data-testid="pause"]')
        print("⏸️ 일시정지")
        page.wait_for_timeout(1000)

        download_btn = page.locator('[data-testid="download"]')
        expect(download_btn).to_be_visible(timeout=2000)
        assert download_btn.is_disabled(), "❌ 일시정지 후 다운로드 버튼이 비활성화 상태여야 함"
        print("🚫 다운로드 버튼 비활성화 상태 확인 (일시정지 후)")

        # ✅ 재개
        page.click('[data-testid="start"]')
        print("▶️ 재개")
        page.wait_for_timeout(10000)

        # ✅ 종료
        page.click('[data-testid="stop"]')
        page.wait_for_timeout(1000)
        page.click('[data-testid="btn_confirm"]')
        page.wait_for_timeout(2000)
        print("⏹️ 녹취 종료")

        # ✅ 다운로드 버튼 활성화 확인
        expect(download_btn).to_be_enabled(timeout=3000)
        print("✅ 다운로드 버튼 활성화 확인")

        # ✅ 다운로드 실행
        with page.expect_download() as download_info:
            download_btn.click()
        download = download_info.value
        file_path = download.path()
        file_name = download.suggested_filename
        print(f"📁 다운로드 파일명: {file_name}")

        assert file_path is not None and os.path.exists(file_path), "❌ 다운로드된 파일이 존재하지 않음"
        assert any(file_name.endswith(ext) for ext in ALLOWED_EXTENSIONS), f"❌ 허용되지 않은 확장자: {file_name}"
        print("🎧 다운로드 파일 유효성 검사 통과")

        # ✅ 녹취 취소 시나리오
        page.goto(URLS["cen_record"])
        page.wait_for_timeout(2000)
        page.click('[data-testid="start"]')
        page.wait_for_timeout(10000)
        page.click('[data-testid="cancel"]')
        page.wait_for_timeout(1000)
        page.click('[data-testid="btn_confirm"]')
        print("❌ 녹취 취소")

        download_btn_after_cancel = page.locator('[data-testid="download"]')
        expect(download_btn_after_cancel).to_be_visible(timeout=3000)
        assert download_btn_after_cancel.is_disabled(), "❌ 취소 후 다운로드 버튼이 활성 상태입니다."
        print("🚫 취소 후 다운로드 버튼 비활성화 상태 확인")

    #     # ✅ 성공 시 Slack 알림 전송
    #     send_custom_slack_message(
    #         pass_items=[
    #             "녹취 진행 및 취소, 종료 확인",
    #             "녹취 파일 다운로드 및 파일 형식 확인"
    #         ],
    #         fail_items=[]
    #     )

    # except AssertionError as e:
    #     # ❌ 실패 시 Slack 알림 전송
    #     send_custom_slack_message(
    #         pass_items=[],
    #         fail_items=["녹취 자동화 테스트 실패"],
    #         fail_reason=str(e)
    #     )
    #     raise
    # except Exception as e:
    #     # ❌ 기타 예외도 Slack 알림
    #     send_custom_slack_message(
    #         pass_items=[],
    #         fail_items=["녹취 자동화 테스트 오류"],
    #         fail_reason=str(e)
    #     )
    #     raise