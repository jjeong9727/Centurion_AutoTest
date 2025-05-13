def test_register_multiple_customers():
    from helpers.customer_utils import add_customer_to_json

    # 고객 등록 프로세스 추가 필요

    # 각 함수 명으로 변경 및 루프 설정 필요

    customers = [
        {
            "customer_name": "김하나",
            "chart_id": "CHT101",
            "birth": "1992-03-14",
            "gender": "여",
            "phone": "010-1000-0001",
            "email": "hana@test.com",
            "nationality": "대한민국",
            "grade" : "VIP",
            "amount": 100000,
            "mileage": 2000,
            "balance": 98000
        },
        {
            "customer_name": "이둘",
            "chart_id": "CHT102",
            "birth": "1985-07-22",
            "gender": "남",
            "phone": "010-1000-0002",
            "email": "dul@test.com",
            "nationality": "대한민국",
            "grade" : "VIP",
            "amount": 200000,
            "mileage": 5000,
            "balance": 195000
        }
    ]

    for c in customers:
        add_customer_to_json(c)
