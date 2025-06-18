import json
import os
import re

# 테스트 이름 한글 매핑
full_name_mapping = {
    # centurion
    "test_cen_customer_edit": "Centurion 고객 정보 수정 확인",
    "test_cen_customer_search": "Centurion 고객 검색 기능 확인",
    "test_cen_customer_register": "Centurion 고객 등록 확인",
    "test_cen_grade": "Centurion 등급 관리 기능 확인",
    "test_cen_login": "Centurion 로그인 유효성 확인",
    "test_cen_membership": "Centurion 멤버십 충전/차감 확인",
    "test_cen_reservation_accept": "Centurion 예약 확정/취소 확인",
    "test_cen_reservation_edit": "Centurion 예약 정보 수정 확인",
    "test_cen_reservation_register": "Centurion 예약 추가 확인",
    "test_cen_reservation_search": "Centurion 예약 검색 확인",
    "test_cen_record": "Centurion 녹취 확인",

    # home
    "test_home_landing_login": "로그인 진입 확인",
    "test_home_landing_nologin": "비로그인 진입 시도 확인",
    "test_home_language": "다국어 확인",
    "test_home_reservation": "예약 신청 확인"
}
category_prefix = {
    "login": "로그인",
    "language": "다국어",
    "membership": "멤버십 충전차감",
    "customer": "고객관리",
    "grade": "멤버십 등급관리",
    "reservation": "예약관리",
    "landng": "홈페이지 진입 확인",
    "record" : "녹취"
}

# 예쁜 이름
def prettify_name(raw_name):
    readable = full_name_mapping.get(raw_name, raw_name)
    match = re.match(r"test_(?:centurion|home)?_?([a-z]+)", raw_name)
    category_key = match.group(1) if match else "etc"
    category = category_prefix.get(category_key, "기타")
    return f"[자동화] {readable} 테스트"

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