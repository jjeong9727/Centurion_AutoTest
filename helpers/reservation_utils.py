import json
import os
from datetime import datetime
import random
from playwright.sync_api import Page, expect

RESERVATION_FILE = "data/reservations.json"
# 예약 추가 후 json 파일에 내역 생성
def save_reservation_to_json(reservation: dict, file_path=RESERVATION_FILE):
    data = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                pass
    data.append(reservation)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# json 파일 최근 추가된 내역 3개 추출
def load_recent_reservations(count=3, file_path="data/reservations.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        reservations = json.load(f)
    return reservations[-count:]  # 마지막 3개 반환

#예약 내역 검색 및 데이터 싱크 확인
def verify_multiple_reservations_in_list(page: Page, count=4):
    reservations = load_recent_reservations(count)
    for res in reservations:
        page.fill('[data-testid="search_name"]', res["name"])
        page.locator("body").click()

        row = page.locator("table tbody tr").first
        cells = row.locator("td")

        assert cells.nth(1).inner_text().strip() == res["status"], "❌ 예약 상태 불일치"
        assert cells.nth(2).inner_text().strip() == res["name"], "❌ 이름 불일치"
        assert cells.nth(3).inner_text().strip() == res["birth"], "❌ 생년월일 불일치"
        assert cells.nth(4).inner_text().strip() == res["gender"], "❌ 성별 불일치"
        assert cells.nth(5).inner_text().strip() == res["phone"], "❌ 전화번호 불일치"
        assert cells.nth(6).inner_text().strip() == res["email"], "❌ 이메일 불일치"
        assert cells.nth(7).inner_text().strip() == res["datetime"], "❌ 예약일시 불일치"

        print(f"✅ 등록 확인 완료: {res['name']}")

#예약 확정 / 취소 시 예약 상태 업데이트
def update_reservation_status(name, new_status):
    if not RESERVATION_FILE.exists():
        return

    with open(RESERVATION_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    for res in data:
        if res["name"] == name:
            res["status"] = new_status
            break

    with open(RESERVATION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 예약 상태에 해당하는 내역 불러오기
def get_reservations_by_status(status):
    if not RESERVATION_FILE.exists():
        return []

    with open(RESERVATION_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [res for res in data if res.get("status") == status]
