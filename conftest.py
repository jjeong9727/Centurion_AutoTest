import pytest
from playwright.sync_api import sync_playwright
from helpers.language_mapping import generate_language_json

@pytest.fixture(scope="session", autouse=True)
def prepare_language_mapping():
    generate_language_json()  # language.json 생성

@pytest.fixture(scope="function")
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 또는 True로 설정 가능
        context = browser.new_context()
        page = context.new_page()
        yield page
        context.close()
        browser.close()
