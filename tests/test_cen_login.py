# Centurion 로그인 테스트
# ID/PW 미입력 | 불일치 | 정상 로그인 확인

import pytest
import os
import json
from playwright.sync_api import Page, expect
from config import Account, URLS
file_path = os.path.join(os.path.dirname(__file__), "version_info.json")
def test_login_flow(page: Page):
    # 1. 로그인 페이지 진입
    page.goto(URLS["cen_login"])
    page.wait_for_timeout(2000)

    # 2. 입력 필드 노출 확인
    expect(page.locator('[data-testid="input_id"]')).to_be_visible()
    page.wait_for_timeout(500)
    expect(page.locator('[data-testid="input_pw"]')).to_be_visible()
    page.wait_for_timeout(500)

    # 3. 아이디만 입력 → 로그인 버튼 비활성화 확인
    page.fill('[data-testid="input_id"]', Account["testid"])
    page.wait_for_timeout(1000)
    expect(page.locator('[data-testid="btn_login"]')).to_be_disabled()
    page.wait_for_timeout(1000)

    # 4. 잘못된 비밀번호 입력 → 불일치 문구 노출 확인
    page.fill('[data-testid="input_pw"]', Account["wrongpw"])
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_login"]')
    expect(page.locator('[data-testid="alert_wrong_pw"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    # 5. 올바른 비밀번호 입력 → 로그인 성공 및 메인 진입 확인
    page.fill('[data-testid="input_pw"]', Account["testpw"])
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_login"]')
    page.wait_for_timeout(2000)
    page.wait_for_url(URLS["cen_main"])
    page.wait_for_timeout(500)
    expect(page.locator("text=로그아웃")).to_be_visible()
    page.wait_for_timeout(2000)

    # 테스트 버전 가져오기
    version_span = page.locator("text=메디솔브에이아이(주)").locator("xpath=following-sibling::span")
    version_text = version_span.text_content().strip().splitlines()[-1].strip().strip('"')

    print(f"버전: {version_text}")

    version_data = {
        "version_cen": version_text
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({"version_cen": version_text}, f, ensure_ascii=False, indent=2)


    # 로그아웃 절차 → 토스트 확인 및 로그인 화면 이동 확인
    page.click('[data-testid="btn_logout"]')
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_confirm"]')
    expect(page.locator('[data-testid="toast_logout"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    expect(page.locator('[data-testid="input_id"]')).to_be_visible(timeout=5000)
