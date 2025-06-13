import os
import json
import random
from datetime import datetime, timedelta
from playwright.sync_api import Page  
from config import URLS, Account

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
        if customer["name"] == customer_name:
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

    return customer_name 
    # return f"자동화테스트" 
def generate_random_birth():
    start = datetime.strptime("1960-01-01", "%Y-%m-%d")
    end = datetime.strptime("2004-12-31", "%Y-%m-%d")
    return (start + timedelta(days=random.randint(0, (end - start).days))).strftime("%Y-%m-%d")
def generate_random_phone():
    return f"010-{random.randint(1000,9999):04}-{random.randint(1000,9999):04}"
    # return f"010-6275-4153"
def generate_random_email():
    prefix = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=8)) 
    return f"{prefix}@test.com" 
    # return f"jekwon@medisolveai.com"
def generate_random_customer():
    return {
        "customer_name": generate_customer_name(),
        "birth": generate_random_birth(),
        "gender": random.choice(["남성", "여성"]),
        "phone": generate_random_phone(),
        "email": generate_random_email()
    }


# Centurion 로그인 동작
def cen_login(page: Page):
    page.goto(URLS["cen_login"])
    page.wait_for_timeout(2000)
    page.fill('[data-testid="input_id"]', Account["testid"])
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_pw"]', Account["testpw"])
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_login"]')
    page.wait_for_timeout(2000)
    page.wait_for_url(URLS["cen_main"])
    page.wait_for_timeout(500)