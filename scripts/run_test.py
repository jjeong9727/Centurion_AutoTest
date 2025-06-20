import os
import json
import subprocess
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

from scripts.register_issue import process_issues
from scripts.send_slack import send_slack_message

TEST_RESULTS_FILE = "test_results.json"
JSON_REPORT_FILE = "scripts/result.json"
SUMMARY_FILE = "scripts/summary.json"
DEVICE_PROFILE_FILE = Path(__file__).resolve().parent.parent / "tests" / "device_profile.json"

# 초기화
for path in [TEST_RESULTS_FILE, JSON_REPORT_FILE, SUMMARY_FILE]:
    if os.path.exists(path):
        os.remove(path)
        print(f"🎩 기존 파일 제거: {path}")

# 디바이스 목록 로드
with open(DEVICE_PROFILE_FILE, encoding="utf-8") as f:
    DEVICE_PROFILES = json.load(f)

devices = list(DEVICE_PROFILES.keys())

# 테스트 결과 저장 함수
def save_test_result(test_name, message, status="FAIL", file_name=None, stack_trace="", duration=None, device=None):
    result_data = {
        "test_name": test_name,
        "status": status,
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "file": file_name,
        "stack": stack_trace,
        "duration": duration,
        "device": device
    }

    if os.path.exists(TEST_RESULTS_FILE):
        with open(TEST_RESULTS_FILE, 'r', encoding='utf-8') as f:
            results = json.load(f)
    else:
        results = []

    results.append(result_data)

    with open(TEST_RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


# ✅ 모바일/PC 모두 실행할 테스트
mobile_supported_tests = [
    # "tests/test_home_landing_nologin.py",
    # "tests/test_home_landing_login.py",
    # "tests/test_home_language.py"
]

# ✅ PC에서만 실행할 테스트
pc_only_tests = [
    # "tests/test_home_reservation.py",
    # "tests/test_cen_login.py",
    # "tests/test_cen_customer_register.py",
    # "tests/test_cen_customer_edit.py",
    # "tests/test_cen_customer_search.py",
    # "tests/test_cen_grade.py",
    # "tests/test_cen_membership.py",
    # "tests/test_cen_reservation_accept.py",
    # "tests/test_cen_reservation_edit.py",
    # "tests/test_cen_reservation_search.py",
    # "tests/test_cen_reservation_register.py",
    # "tests/test_cen_record.py"
]

# 전체 리스트는 아래에서 사용
all_tests = mobile_supported_tests + pc_only_tests


# 테스트 실행
for device in devices:
    os.environ["TEST_DEVICE"] = device
    print(f"\n🌐 디바이스: {device} 테스트 시작")

    for test_file in all_tests:
        # ✅ PC 전용 테스트는 Windows에서만 실행
        if test_file in pc_only_tests and "Windows" not in device:
            continue


        test_name = os.path.splitext(os.path.basename(test_file))[0]
        print(f"\n🚀 {test_file} 테스트 실행 중...")

        start_time = datetime.now()
        try:
            result = subprocess.run(
                ["pytest", test_file, "--json-report"],
                capture_output=True,
                text=True,
                check=True
            )
            duration = (datetime.now() - start_time).total_seconds()
            print(f"✅ {test_file} 테스트 완료")
            save_test_result(
                test_name=test_name,
                message="테스트 성공",
                status="PASS",
                file_name=test_file,
                duration=f"{duration:.2f}초",
                device=device
            )
        except subprocess.CalledProcessError as e:
            duration = (datetime.now() - start_time).total_seconds()
            full_output = e.stderr or e.stdout or "출력 없음"

            error_lines = full_output.strip().splitlines()
            parsed_message = ""
            for line in reversed(error_lines):
                if any(x in line for x in ["Error", "Exception", "Traceback", "Assertion"]):
                    parsed_message = line.strip()
                    break
            if not parsed_message and error_lines:
                parsed_message = error_lines[-1].strip()

            print(f"❌ {test_file} 테스트 실패")
            save_test_result(
                test_name=test_name,
                message=parsed_message,
                status="FAIL",
                file_name=test_file,
                stack_trace=full_output,
                duration=f"{duration:.2f}초",
                device=device
            )

print("\n🎯 모든 테스트 완료")

# 결과 파싱 (summary_.json, jira_issues.json 생성)
subprocess.run(["python", "scripts/parse.py"])

# Jira 이슈 처리 및 이슈 키 매핑 반환
jira_issues_path = "scripts/jira_issues.json"
if os.path.exists(jira_issues_path) and os.path.getsize(jira_issues_path) > 0:
    issue_map = process_issues(jira_issues_path)  # ex: ["CEN-123", "HOME-456"]
else:
    issue_map = []

# Slack 알림 전송 (이슈 키 포함)
subprocess.run(["python", "scripts/send_slack.py", json.dumps(issue_map, ensure_ascii=False)])

# Slack 알림 전송
send_slack_message(issue_map)
