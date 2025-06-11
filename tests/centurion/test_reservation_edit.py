# 테스트 흐름
# 1. 예약 관리 화면에서 각 항목 선택
# 2. 데이터 값 삭제 후 유효성 체크
# 3. 정상 데이터 입력 후 수정 확인
from playwright.sync_api import Page, expect
from datetime import datetime, timedelta
from config import URLS
from helpers.customer_utils import cen_login

def test_editable_columns_by_status(page: Page):
    # 상태별 수정 가능 열 정의 (예약일 8열, 직원 메모 10열)
    status_editable_columns = {
        "대기": [8, 10],
        "확정": [8, 10],
        "취소": [10],
        "완료": [10]
    }

    for status, editable_cols in status_editable_columns.items():
        print(f"\n🔍 상태: {status} - 수정테스트 고객 예약 검색 시작")

        cen_login(page) # 로그인
        # 상태 + 이름 검색
        page.goto(URLS["cen_reservation"])
        page.get_by_test_id("search_status").select_option(label=status)
        page.fill('[data-testid="search_name"]', "수정테스트")
        page.click("body")

        rows = page.locator("table tbody tr")
        row_count = rows.count()

        if row_count == 0:
            print(f"⚠️ 상태 '{status}'의 검색 결과가 없습니다.")
            continue
        elif row_count > 1:
            print(f"⚠️ 상태 '{status}' 검색 결과가 {row_count}건입니다. 첫 번째 예약만 수정합니다.")

        # 첫 번째 예약 행 선택
        row = rows.first

        # ✅ 예약일 (8열 = nth(7))
        if 8 in editable_cols:
            date_cell = row.locator("td").nth(7)
            date_cell.click()

            # 오늘 +1일 선택
            tomorrow = datetime.today() + timedelta(days=1)
            day = tomorrow.day
            date_selector = f'[data-testid="btn_day_{day}"]'
            page.click(date_selector)

            # 가장 이른 활성화된 시간 버튼 선택
            time_buttons = page.locator('[data-testid^="btn_time_"]')
            found = False
            for i in range(time_buttons.count()):
                btn = time_buttons.nth(i)
                if btn.is_enabled():
                    btn.click()
                    print(f"✅ 선택된 시간: {btn.inner_text()}")
                    found = True
                    break

            assert found, "❌ 선택 가능한 시간이 없습니다."
            page.click("body")

            # 결과 확인
            updated_date = date_cell.inner_text().strip()
            assert str(day) in updated_date, f"❌ {status} 예약일 수정 반영 실패"
            print(f"✅ 예약일 수정 완료 및 확인됨: {updated_date}")
        else:
            print(f"⏭️ {status} 상태에서는 예약일 수정 불가")

        # ✅ 직원 메모 (10열 = nth(9))
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
