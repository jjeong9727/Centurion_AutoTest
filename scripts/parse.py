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
    "landng": "홈페이지 진입",
    "record" : "녹취"
}

# 예쁜 이름
def prettify_name(raw_name):
    readable = full_name_mapping.get(raw_name, raw_name)
    match = re.match(r"test_(?:centurion|home)?_?([a-z]+)", raw_name)
    category_key = match.group(1) if match else "etc"
    category = category_prefix.get(category_key, "기타")
    return f"{readable} 테스트"
def normalize_summary(name):
    return re.sub(r"\s+", " ", name.strip())
# stack 요약 생성
def summarize_stack(stack):
    if not stack:
        return ""
    lines = stack.strip().splitlines()
    file_lines = [line for line in lines if line.strip().startswith("File")]
    last_file_line = file_lines[-1] if file_lines else ""
    last_line = lines[-1] if lines else ""
    return f"{last_file_line.strip()} → {last_line.strip()}"

def generate_jira_payload(result_item):
    # 프로젝트 키 결정
    file_name = result_item['file']
    if "test_cen_" in file_name:
        project_key = "CEN"
    elif "test_home_" in file_name:
        project_key = "HOME"
    else:
        project_key = "TEST"  # 기본값

    # 써머리는 한글 매핑된 이름을 사용
    raw_summary = normalize_summary(result_item["name"])
    summary = f"[자동화] {raw_summary}"

    return {
        "summary": summary,
        "description": (
            f"에러 메시지: {result_item['message']}\n\n"
            f"파일: {result_item['file']}\n"
            f"테스트 이름: {result_item['name']}\n\n"
            f"스택 요약:\n{result_item['stack_summary']}"
        ),
        "project": project_key,
        "issuetype": "Bug",
        "priority": "Medium",
        "labels": ["auto-test", "fail"],
        "file": result_item.get("file", "")
    }


def extract_results(input_path="test_results.json", output_path="scripts/summary_.json", jira_output_path="scripts/jira_issues.json"):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = []
    jira_issues = []

    for item in data:
        test_name = item.get("test_name", "")
        status = item.get("status", "")
        message = item.get("message", "")
        stack = item.get("stack", "")

        if status == "FAIL":
            first_line = message.strip().splitlines()[0] if isinstance(message, str) else message
            stack_summary = summarize_stack(stack)
        else:
            first_line = "테스트 성공"
            stack_summary = ""

        entry = {
            "name": prettify_name(test_name),
            "file": item.get("file", ""),
            "status": status,
            "message": first_line,
            "stack_summary": stack_summary
        }
        result.append(entry)

        if status == "FAIL":
            jira_issues.append(generate_jira_payload(entry))

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    with open(jira_output_path, "w", encoding="utf-8") as f:
        json.dump(jira_issues, f, indent=2, ensure_ascii=False)

    print(f"✅ summary_.json 저장 완료 ({len(result)}건)")
    print(f"🐞 Jira 이슈용 payload 저장 완료 ({len(jira_issues)}건)")


if __name__ == "__main__":
    extract_results()
