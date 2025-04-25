# conftest.py
import pytest
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from typing import Generator

@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as playwright:
        yield playwright

@pytest.fixture(scope="session")
def browser(playwright_instance) -> Generator[Browser, None, None]:
    # browser = playwright_instance.chromium.launch(headless=False)  # 브라우저 ON
    browser = playwright_instance.chromium.launch(headless=True)  # 브라우저 OFF
    yield browser
    browser.close()

@pytest.fixture(scope="function")
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    context = browser.new_context()
    yield context
    context.close()

@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Generator[Page, None, None]:
    page = context.new_page()
    yield page
    page.close()
