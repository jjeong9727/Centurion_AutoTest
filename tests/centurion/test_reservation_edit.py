# 테스트 흐름
# 1. 예약 관리 화면에서 각 항목 선택
# 2. 데이터 값 삭제 후 유효성 체크
# 3. 정상 데이터 입력 후 수정 확인
from playwright.sync_api import Page, expect
from config import URLS

def test_edit_reservation_fields_validation(page: Page):
    page.goto(URLS["cen_res_history"])  

    row = page.locator("table tbody tr").first

    # 필수 필드 (텍스트 입력): 고객명, 생년월일, 전화번호, 이메일
    text_fields = {
        2: ("고객명", "테스터"),
        3: ("생년월일", "1990-01-01"),
        5: ("전화번호", "010-1234-5678"),
        6: ("이메일", "test@example.com")
    }

    for col_idx, (label, valid_input) in text_fields.items():
        cell = row.locator("td").nth(col_idx)

        # 빈값 입력 후 토스트 확인
        cell.click()
        cell.locator("input").fill("")
        page.locator("body").click()
        expect(page.locator('[data-testid="toast_required"]')).to_be_visible(timeout=3000)
        print(f"✅ {label} 빈값 유효성 확인됨")

        # 정상값 입력
        cell.click()
        cell.locator("input").fill(valid_input)
        page.click("body")

        # 수정된 값 확인
        updated_text = cell.inner_text().strip()
        assert valid_input in updated_text, f"❌ {label} 수정값 반영 실패 (기대: {valid_input}, 실제: {updated_text})"
        print(f"✅ {label} 정상 수정 및 반영 확인됨: {updated_text}")

    # 성별 (5열)
    gender_cell = row.locator("td").nth(4)
    gender_cell.click()
    gender_cell.locator("select").select_option(label="여성")  # 실제 옵션 label 확인
    page.click("body")

    updated_gender = gender_cell.inner_text().strip()
    assert "여성" in updated_gender, "❌ 성별 수정 반영 실패"
    print(f"✅ 성별 수정 완료 및 반영 확인됨: {updated_gender}")

    # 예약일 (8열)
    date_cell = row.locator("td").nth(7)
    date_cell.click()
    page.click('[data-testid="btn_day_15"]')
    page.click("body")

    updated_date = date_cell.inner_text().strip()
    assert "15" in updated_date, "❌ 예약일 수정 반영 실패"
    print(f"✅ 예약일 수정 완료 및 반영 확인됨: {updated_date}")

    # 메모 (9열) – 빈값 → '-' → 정상값
    memo_cell = row.locator("td").nth(8)
    memo_cell.click()
    memo_cell.locator("textarea").fill("")
    page.click("body")

    updated_memo = memo_cell.inner_text().strip()
    assert updated_memo == "-", "❌ 메모 빈값 수정 시 '-'로 반영되지 않음"
    print("✅ 메모 빈값 처리 확인 ('-' 노출)")

    memo_cell.click()
    memo_cell.locator("textarea").fill("자동화 테스트 메모")
    page.click("body")

    final_memo = memo_cell.inner_text().strip()
    assert "자동화 테스트 메모" in final_memo, f"❌ 메모 정상 수정 실패 (기대: 자동화 테스트 메모, 실제: {final_memo})"
    print(f"✅ 메모 수정 완료 및 반영 확인됨: {final_memo}")