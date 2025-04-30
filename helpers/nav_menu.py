from playwright.sync_api import Page, expect
from config import URLS

def navigate_all_menus(page: Page, base_url: str):
    """대분류 > 중분류 > 소분류 메뉴를 순차적으로 클릭하고, 페이지 타이틀을 검증하는 함수 (모바일 스크롤 고려 포함)"""

    page.goto(base_url)
    page.wait_for_timeout(1000)

    is_mobile = getattr(page, "is_mobile", False)

    # 대분류 메뉴
    primary_menus = page.locator("[data-testid='menu_1']")
    primary_count = primary_menus.count()

    for i in range(primary_count):
        page.goto(base_url)
        page.wait_for_timeout(1000)

        primary_menus = page.locator("[data-testid='menu_1']")
        if is_mobile:
            primary_menus.nth(i).scroll_into_view_if_needed()
        primary_text = primary_menus.nth(i).inner_text().strip()
        primary_menus.nth(i).click()
        page.wait_for_timeout(1000)

        # 중분류 메뉴
        secondary_menus = page.locator("[data-testid='menu_2']")
        secondary_count = secondary_menus.count()

        for j in range(secondary_count):
            page.goto(base_url)
            page.wait_for_timeout(1000)

            primary_menus = page.locator("[data-testid='menu_1']")
            if is_mobile:
                primary_menus.nth(i).scroll_into_view_if_needed()
            primary_menus.nth(i).click()
            page.wait_for_timeout(1000)

            secondary_menus = page.locator("[data-testid='menu_2']")
            if is_mobile:
                secondary_menus.nth(j).scroll_into_view_if_needed()
            secondary_text = secondary_menus.nth(j).inner_text().strip()
            secondary_menus.nth(j).click()
            page.wait_for_timeout(1000)

            # 소분류 메뉴
            tertiary_menus = page.locator("[data-testid='menu_3']")
            tertiary_count = tertiary_menus.count()

            for k in range(tertiary_count):
                page.goto(base_url)
                page.wait_for_timeout(1000)

                primary_menus = page.locator("[data-testid='menu_1']")
                if is_mobile:
                    primary_menus.nth(i).scroll_into_view_if_needed()
                primary_menus.nth(i).click()
                page.wait_for_timeout(1000)

                secondary_menus = page.locator("[data-testid='menu_2']")
                if is_mobile:
                    secondary_menus.nth(j).scroll_into_view_if_needed()
                secondary_menus.nth(j).click()
                page.wait_for_timeout(1000)

                tertiary_menus = page.locator("[data-testid='menu_3']")
                if is_mobile:
                    tertiary_menus.nth(k).scroll_into_view_if_needed()
                tertiary_text = tertiary_menus.nth(k).inner_text().strip()

                tertiary_menus.nth(k).click()
                page.wait_for_timeout(1000)

                # 페이지 타이틀 가져오기
                page_title = page.locator("[data-testid='txt_title']").inner_text().strip()

                try:
                    assert tertiary_text == page_title, (
                        f"❌ 실패! 대분류({primary_text}) > 중분류({secondary_text}) > 소분류({tertiary_text}) 메뉴에서 "
                        f"페이지 타이틀 '{page_title}' 불일치"
                    )
                    print(f"✅ 성공: {primary_text} > {secondary_text} > {tertiary_text}")
                except AssertionError as e:
                    raise e
