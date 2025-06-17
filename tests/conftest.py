import sys, os, json
import pytest
from pathlib import Path
from typing import Generator
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from pathlib import Path

# 상대경로 상위 디렉토리 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 디바이스 설정 로드
DEVICE_JSON_PATH = Path(__file__).parent / "device_profile.json"
with open(DEVICE_JSON_PATH, encoding="utf-8") as f:
    DEVICE_PROFILES = json.load(f)

@pytest.fixture(scope="session")
def browser() -> Generator[Browser, None, None]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()

@pytest.fixture(params=list(DEVICE_PROFILES.keys()))
def device_profile(request):
    return DEVICE_PROFILES[request.param]

@pytest.fixture
def context(browser: Browser, device_profile) -> Generator[BrowserContext, None, None]:
    context = browser.new_context(
        viewport=device_profile["viewport"],
        device_scale_factor=device_profile["device_scale_factor"],
        is_mobile=device_profile["is_mobile"],
        has_touch=device_profile["has_touch"],
        user_agent=device_profile["user_agent"],
        permissions=["microphone"]
    )
    yield context
    context.close()

@pytest.fixture
def page(context: BrowserContext) -> Generator[Page, None, None]:
    page = context.new_page()
    yield page
    page.close()


@pytest.fixture(scope="session")
def launch_options():
    return {
        "args": [
            "--use-fake-ui-for-media-stream",     # 🎤 마이크 권한 팝업 없이 자동 승인
            "--use-fake-device-for-media-stream", # 🎙️ 가상 마이크 장치로 대체
        ]
    }