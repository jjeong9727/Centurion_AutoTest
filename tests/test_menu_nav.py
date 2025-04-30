import json
from playwright.sync_api import sync_playwright
from config import URLS
from helpers.nav_menu import navigate_all_menus

# 디바이스 프로필 불러오기
with open("data/device_profiles.json", "r", encoding="utf-8") as f:
    device_profiles = json.load(f)

def is_ios_device(profile: dict) -> bool:
    ua = profile.get("user_agent", "")
    return "iPhone" in ua or "iOS" in ua

def run_menu_navigation_test(device_name: str, profile: dict):
    from helpers.auth_helper import ensure_valid_token

    with sync_playwright() as p:
        browser = (
            p.webkit.launch(headless=False)
            if is_ios_device(profile)
            else p.chromium.launch(headless=False)
        )

        context = browser.new_context(**profile)

        # ✅ access_token 세팅 추가
        access_token = ensure_valid_token()
        context.add_cookies([{
            "name": "access_token",
            "value": access_token,
            "domain": "your-domain.com",  # 테스트 서버 도메인
            "path": "/",
            "httpOnly": True,
            "secure": True,
            "sameSite": "Lax"
        }])

        page = context.new_page()

        # 디바이스 정보 주입
        page.device_name = device_name
        page.is_mobile = profile.get("is_mobile", False)
        page.is_ios = is_ios_device(profile)
        page.is_android = "Android" in profile.get("user_agent", "")

        # 메인 페이지 진입 후 메뉴 이동 및 타이틀 검증
        navigate_all_menus(page, base_url=URLS["home_main"])

        browser.close()


def test_all_device_menu_navigation():
    for device_name, profile in device_profiles.items():
        print(f"\n🚀 [START] {device_name} 메뉴 진입 테스트")
        run_menu_navigation_test(device_name, profile)
        print(f"✅ [PASS] {device_name} 완료\n")

# 메인 실행
if __name__ == "__main__":
    test_all_device_menu_navigation()
