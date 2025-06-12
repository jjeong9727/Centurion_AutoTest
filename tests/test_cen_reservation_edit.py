# 테스트 흐름
# 1. 예약 정보 에서 예약일자 시간 메모 수정
# 2. 홈페이지 노출 형식에 맞춰 재가공
# 3. 홈페이지 마이페이지 진입 하여 수정 반영 체크
from playwright.sync_api import Page
from config import URLS
from helpers.customer_utils import cen_login
from helpers.homepage_utils import get_available_time_button, get_reservation_datetime
from helpers.reservation_utils import update_reservation_info
from helpers.auth_helper import login_with_token
from datetime import datetime
import locale
import json

# 한국어 요일 설정
locale.setlocale(locale.LC_TIME, "ko_KR.UTF-8")

def load_reservation_data(json_path="data/reservation.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data[0] if data else None

def convert_to_homepage_date_format(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y.%m.%d")
    return dt.strftime("%Y-%m-%d %a")  # 예: 2025-06-14 토

def convert_name_to_home_format(name: str) -> str:
    if "(" in name and ")" in name:
        visitor, booker = name.split("(")
        booker = booker.replace(")", "")
        return f"{booker}({visitor})"
    return name

def verify_homepage_display(page: Page, reservation: dict):
    from playwright.sync_api import expect

    expected_name = convert_name_to_home_format(reservation["name"])
    expected_date = convert_to_homepage_date_format(reservation["date"])
    expected_time = reservation["time"]

    rows = page.locator('[data-testid="table_history"] tbody tr')
    found = False

    for i in range(rows.count()):
        row = rows.nth(i)
        cells = row.locator("td")

        actual_date = cells.nth(0).inner_text().strip()
        actual_time = cells.nth(1).inner_text().strip()
        actual_name = cells.nth(2).inner_text().strip()

        if (actual_date == expected_date and
            actual_time == expected_time and
            actual_name == expected_name):
            found = True
            print(f"✅ 홈페이지에 수정된 예약 정보가 정상 반영됨 (행 {i+1})")
            break

    assert found, (
        f"❌ 수정된 예약 정보가 홈페이지에 표시되지 않음\n"
        f"→ 기대값: {expected_date}, {expected_time}, {expected_name}"
    )


def test_editable_columns_by_status(page: Page):
    # ✅ 예약 정보 1회 로딩
    reservation = load_reservation_data()
    assert reservation, "❌ reservation.json에서 예약 정보를 불러올 수 없습니다."

    name = reservation["name"]
    original_reservation = reservation.copy()  # 원본 저장 (재가공용)

    updated_date = reservation["date"]
    updated_time = reservation["time"]
    updated_memo = reservation["memo"]

    status_editable_columns = {
        "대기": [8, 10],
        "확정": [8, 10],
        "취소": [10],
        "완료": [10]
    }

    for status, editable_cols in status_editable_columns.items():
        print(f"\n🔍 상태: {status} - 예약자 '{name}' 검색 시작")

        cen_login(page)
        page.goto(URLS["cen_reservation"])
        page.get_by_test_id("search_status").select_option(label=status)
        page.fill('[data-testid="search_name"]', name)
        page.click("body")

        rows = page.locator("table tbody tr")
        row_count = rows.count()

        if row_count == 0:
            print(f"⚠️ 상태 '{status}'의 검색 결과가 없습니다.")
            continue
        elif row_count > 1:
            print(f"⚠️ 상태 '{status}' 검색 결과가 {row_count}건입니다. 첫 번째 예약만 수정합니다.")

        row = rows.first

        # ✅ 예약일 수정
        if 8 in editable_cols:
            date_cell = row.locator("td").nth(7)
            date_cell.click()
            page.wait_for_timeout(2000)

            date = get_reservation_datetime(page)
            time_str = get_available_time_button(page)
            updated_date = date["date"]
            updated_time = time_str
            print(f"✅ 예약일 수정 완료 및 확인됨: {updated_date} / {updated_time}")
            page.wait_for_timeout(2000)
        else:
            print(f"⏭️ {status} 상태에서는 예약일 수정 불가")

        # ✅ 직원 메모 수정
        if 10 in editable_cols:
            memo_cell = row.locator("td").nth(9)
            memo_cell.click()
            memo_cell.locator("textarea").fill("자동화 메모 수정")
            page.click("body")

            updated_memo = memo_cell.inner_text().strip()
            assert "자동화" in updated_memo, f"❌ {status} 직원메모 수정 반영 실패"
            print(f"✅ 직원메모 수정 완료 및 확인됨: {updated_memo}")
        else:
            print(f"⏭️ {status} 상태에서는 직원메모 수정 불가")

    # ✅ JSON 업데이트
    update_reservation_info(name, f"{updated_date}", updated_memo)

    # ✅ 수정된 값 로컬 객체에 반영
    original_reservation["date"] = updated_date
    original_reservation["time"] = updated_time
    original_reservation["memo"] = updated_memo

    # ✅ 홈페이지 진입 후 정보 확인
    page.goto(URLS["home_main"])
    page.wait_for_timeout(3000)
    login_with_token(page, account_type="google")
    page.goto(URLS["home_mypage_history"])

    verify_homepage_display(page, original_reservation)
