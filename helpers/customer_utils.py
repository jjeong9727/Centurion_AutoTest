import os
import json

def add_customer_to_json(new_customer: dict, file_path="data/customers.json"):
    """고객명 기준으로 중복 없는 경우 전체 신규 고객 정보 추가"""
    customers = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            customers = json.load(f)

    if any(c["customer_name"] == new_customer["customer_name"] for c in customers):
        print(f"❌ 이미 등록된 고객: {new_customer['customer_name']}")
        return

    customers.append(new_customer)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(customers, f, ensure_ascii=False, indent=2)

    print(f"✅ 고객 '{new_customer['customer_name']}' 등록 완료")


def update_customer_in_json(customer_name: str, updates: dict, file_path="data/customers.json"):
    """customer_name 기준으로 일부 필드만 선택적으로 업데이트 (chart_id, balance 제외)"""
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
