import os
import json
import random
from datetime import datetime, timedelta
from playwright.sync_api import Page  # ← 이게 없다면 Page를 알 수 없음

#고객 등록 후 json에 추가  
def add_customer_to_json(new_customer: dict, file_path="data/customers.json"):
    customers = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            customers = json.load(f)

    customers.append(new_customer)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(customers, f, ensure_ascii=False, indent=2)

    print(f"✅ 고객 '{new_customer['customer_name']}' 정보 저장 완료")

# 고객 정보 수정 후 json 업데이트
def update_customer_in_json(customer_name: str, updates: dict, file_path="data/customers.json"):
    if not os.path.exists(file_path):
        print("❌ 고객 데이터 없음")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        customers = json.load(f)

    updated = False
    for customer in customers:
        if customer["customer_name"] == customer_name:
            for key, value in updates.items():
                if key in customer and key not in ["chart_id", "balance"]:
                    customer[key] = value
            updated = True
            break

    if updated:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(customers, f, ensure_ascii=False, indent=2)
        print(f"✅ 고객 '{customer_name}' 정보 수정 완료")
    else:
        print(f"❌ 고객 '{customer_name}' 을 찾을 수 없습니다.")


# 고객 등록 데이터 랜덤 생성 
def generate_customer_name(prefix="자동화", count_file="data/daily_count.json"):
    today = datetime.now().strftime("%m%d")  # 예: "0522"

    # 기존 카운트 파일 로드 또는 초기화
    if os.path.exists(count_file):
        with open(count_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}

    # 날짜별 카운트 증가
    if today not in data:
        data[today] = 1
    else:
        data[today] += 1

    count = data[today]
    customer_name = f"{prefix}-{today}.{count}"

    # 카운트 저장
    with open(count_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # return customer_name #랜덤생성 Pending
    return f"자동화테스트" 
def generate_random_birth():
    start = datetime.strptime("1960-01-01", "%Y-%m-%d")
    end = datetime.strptime("2004-12-31", "%Y-%m-%d")
    return (start + timedelta(days=random.randint(0, (end - start).days))).strftime("%Y-%m-%d")
def generate_random_phone():
    # return f"010-{random.randint(1000,9999):04}-{random.randint(1000,9999):04}" #랜덤생성 Pending
    return f"010-6275-4153"
def generate_random_email():
    # prefix = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=8)) # 랜덤생성 Pending
    # return f"{prefix}@test.com" # 랜덤생성 Pending
    return f"jekwon@medisolveai.com"
def generate_random_customer():
    return {
        "customer_name": generate_customer_name(),
        "birth": generate_random_birth(),
        "gender": random.choice(["남성", "여성"]),
        "phone": generate_random_phone(),
        "email": generate_random_email()
    }



# 페이지네이션으로 등급 찾기
def find_vip_row(page: Page):
    while True:
        rows = page.locator("table tbody tr")
        row_count = rows.count()

        for i in range(row_count):
            row = rows.nth(i)
            page.evaluate("(element) => element.scrollIntoView()", row)  # ✅ 스크롤
            cell_text = row.locator("td").nth(1).inner_text()

            if "VIP" in cell_text:
                return row  # ✅ VIP 등급 행 반환

        # ✅ 다음 페이지 버튼이 활성화돼 있으면 클릭
        next_button = page.locator('[data-testid="page_next"]')
        if next_button.is_enabled():
            next_button.click()
            page.wait_for_timeout(500)  # 페이지 전환 대기
        else:
            break

    return None  # VIP 등급을 찾지 못한 경우