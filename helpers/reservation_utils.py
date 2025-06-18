import json
import os
from datetime import datetime
import random
from playwright.sync_api import Page, expect
from pathlib import Path

RESERVATION_FILE = Path("data/reservation.json")  # ← 문자열 대신 Path 객체로 정의
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
def verify_multiple_reservations_in_list(page: Page, count=1):
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
def get_reservations_by_status(status=str):
    if not RESERVATION_FILE.exists():
        return []

    with open(RESERVATION_FILE, "r", encoding="utf-8") as f:
        reservations = json.load(f)

    return [r for r in reservations if r.get("status") == status]

# 예약 정보 업데이트
def update_reservation_info(name: str, new_date: str,new_time: str, new_memo: str, json_path="data/reservation.json"):
    import json

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated = False
    for item in data:
        if item["name"] == name:
            item["date"] = new_date
            item["time"] = new_time
            item["memo"] = new_memo
            updated = True
            break

    if updated:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ '{name}' 예약일이 {new_date}{new_time} 메모가 '{new_memo}'(으)로 업데이트되었습니다.")
    else:
        print(f"⚠️ '{name}' 예약 정보를 찾을 수 없습니다.")
