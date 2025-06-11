import json
import os
import re

# 테스트 이름 한글 매핑
full_name_mapping = {
    # centurion
    "test_customer_edit": "고객 정보 수정 확인",
    "test_customer_search": "고객 검색 기능 확인",
    "test_customer_validation": "고객 입력값 유효성 검사",
    "test_grade": "등급 관리 기능 확인",
    "test_login": "센트리온 로그인 확인",
    "test_membership": "멤버십 충전/차감 확인",
    "test_reservation_accept": "예약 확정/취소 확인",
    "test_reservation_edit": "예약 정보 수정 확인",
    "test_reservation_register": "예약 추가 확인",
    "test_reservation_search": "예약 검색 확인",

    # home
    "test_landng_login": "홈페이지 로그인 진입 확인",
    "test_landng_nologin": "홈페이지 비로그인 진입 시도 확인",
    "test_language": "홈페이지 다국어 UI 확인",
    "test_membership": "홈페이지 멤버십 안내 확인",
    "test_reservation": "홈페이지 예약 신청 확인",
}

category_prefix = {
    "login": "로그인",
    "language": "다국어",
    "membership": "멤버십 충전차감",
    "customer": "고객관리",
    "grade": "멤버십 등급관리",
    "reservation": "예약관리",
    "landng": "홈페이지 진입 확인",
}

# 예쁜 이름
def prettify_name(raw_name):
    readable = full_name_mapping.get(raw_name, raw_name)
    match = re.match(r"test_(?:centurion|home)?_?([a-z]+)", raw_name)
    category_key = match.group(1) if match else "etc"
    category = category_prefix.get(category_key, "기타")
    return f"[자동화][{category}] {readable} 테스트 실패"

# stack 요약 생성
def summarize_stack(stack):
    if not stack:
        return ""
    lines = stack.strip().splitlines()
    file_lines = [line for line in lines if line.strip().startswith("File")]
    last_file_line = file_lines[-1] if file_lines else ""
    last_line = lines[-1] if lines else ""
    return f"{last_file_line.strip()} → {last_line.strip()}"

def extract_results(input_path="test_results.json", output_path="scripts/summary_.json"):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = []
    for item in data:
        test_name = item.get("test_name", "")
        status = item.get("status", "")
        message = item.get("message", "")
        stack = item.get("stack", "")

        if status == "FAIL":
            # 에러 메시지 첫 줄
            first_line = message.strip().splitlines()[0] if isinstance(message, str) else message
            stack_summary = summarize_stack(stack)
        else:
            first_line = "테스트 성공"
            stack_summary = ""

        result.append({
            "name": prettify_name(test_name),
            "file": item.get("file", ""),
            "status": status,
            "message": first_line,
            "stack_summary": stack_summary
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"✅ summary_.json 저장 완료 ({len(result)}건)")




if __name__ == "__main__":
    extract_results()