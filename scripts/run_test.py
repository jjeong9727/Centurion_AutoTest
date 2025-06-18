import os
import json
import subprocess
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

TEST_RESULTS_FILE = "test_results.json"
JSON_REPORT_FILE = "scripts/result.json"
SUMMARY_FILE = "scripts/summary.json"
DEVICE_PROFILE_FILE = Path(__file__).resolve().parent.parent / "tests" / "device_profile.json"

# 초기화
for path in [TEST_RESULTS_FILE, JSON_REPORT_FILE, SUMMARY_FILE]:
    if os.path.exists(path):
        os.remove(path)
        print(f"🪩 기존 파일 제거: {path}")

# 디바이스 목록 로드
with open(DEVICE_PROFILE_FILE, encoding="utf-8") as f:
    DEVICE_PROFILES = json.load(f)

devices = list(DEVICE_PROFILES.keys())  # 예: ["Windows Chrome", "iPhone 13", ...]

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

# 전체 테스트 목록
all_tests = [
    # Ceramique
    "tests/test_home_landing_login.py",
    "tests/test_home_landing_nologin.py",
    "tests/test_home_language.py",
    "tests/test_home_reservation.py",
    # Centurion
    "tests/test_cen_login.py",
    "tests/test_cen_customer_register.py",
    "tests/test_cen_customer_edit.py",
    "tests/test_cen_customer_search.py",
    "tests/test_cen_grade.py",
    "tests/test_cen_membership.py",
    "tests/test_cen_reservation_accept.py",
    "tests/test_cen_reservation_edit.py",
    "tests/test_cen_reservation_search.py",
    "tests/test_cen_reservation_register.py",
    "tests/test_cen_record.py"
]

# 테스트 실행
for device in devices:
    os.environ["TEST_DEVICE"] = device
    print(f"\n🌐 디바이스: {device} 테스트 시작")
    for test_file in all_tests:
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
                if "Error" in line or "Exception" in line or "Traceback" in line or "Assertion" in line:
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
print("\n📤 슬랙 메시지 전송 중...")
subprocess.run(["python", "scripts/parse.py"])
subprocess.run(["python", "scripts/send_slack.py"])
