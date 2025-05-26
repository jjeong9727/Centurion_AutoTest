# conftest.py
import os
import pytest
from typing import Generator
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
import os
from playwright.sync_api import sync_playwright, BrowserContext
import pytest

@pytest.fixture(scope="function")
def context(playwright):
    is_mobile = os.environ.get("PLAYWRIGHT_IS_MOBILE", "false").lower() == "true"
    device_options = {
        "viewport": {"width": 360, "height": 780},
        "device_scale_factor": 3,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": "모바일용 UA"
    } if is_mobile else {}

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(**device_options)
    yield context
    context.close()
    browser.close()


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as playwright:
        yield playwright

@pytest.fixture(scope="session")
def browser(playwright_instance) -> Generator[Browser, None, None]:
    browser = playwright_instance.chromium.launch(headless=False)  # GUI 표시
    yield browser
    browser.close()

@pytest.fixture(scope="function")
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    # 환경 변수로부터 모바일/PC 설정값 읽기
    viewport_width = int(os.getenv("PLAYWRIGHT_VIEWPORT_WIDTH", "1280"))
    viewport_height = int(os.getenv("PLAYWRIGHT_VIEWPORT_HEIGHT", "720"))
    device_scale_factor = float(os.getenv("PLAYWRIGHT_DEVICE_SCALE", "1"))
    is_mobile = os.getenv("PLAYWRIGHT_IS_MOBILE", "False") == "True"
    has_touch = os.getenv("PLAYWRIGHT_HAS_TOUCH", "False") == "True"
    user_agent = os.getenv("PLAYWRIGHT_USER_AGENT", "")

    context = browser.new_context(
        viewport={"width": viewport_width, "height": viewport_height},
        device_scale_factor=device_scale_factor,
        is_mobile=is_mobile,
        has_touch=has_touch,
        user_agent=user_agent
    )
    yield context
    context.close()

@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Generator[Page, None, None]:
    page = context.new_page()
    yield page
    page.close()
