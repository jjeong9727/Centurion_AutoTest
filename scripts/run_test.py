import os
import json
import subprocess
from datetime import datetime
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

TEST_RESULTS_FILE = "test_results.json"
JSON_REPORT_FILE = "scripts/result.json"
SUMMARY_FILE = "scripts/summary.json"

# 초기화
for path in [TEST_RESULTS_FILE, JSON_REPORT_FILE, SUMMARY_FILE]:
    if os.path.exists(path):
        os.remove(path)
        print(f"🪩 기존 파일 제거: {path}")



# 테스트 결과 저장 함수
def save_test_result(test_name, message, status="FAIL", file_name=None, stack_trace="", duration=None):
    result_data = {
        "test_name": test_name,
        "status": status,
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "file": file_name,
        "stack": stack_trace,
        "duration": duration
    }

    if os.path.exists(TEST_RESULTS_FILE):
        with open(TEST_RESULTS_FILE, 'r', encoding='utf-8') as f:
            results = json.load(f)
    else:
        results = []

    results.append(result_data)

    with open(TEST_RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

# 출고 실패 여부 & 스킵 테스트 저장
stock_out_failed = False
skipped_tests = []

# 전체 테스트 목록
all_tests = [
    # Centurion
    "tests/centurion/test_customer_edit.py",
    "tests/centurion/test_customer_search.py",
    "tests/centurion/test_customer_validation.py",
    "tests/centurion/test_grade.py",
    "tests/centurion/test_login.py",
    "tests/centurion/test_membership.py",
    "tests/centurion/test_reservation_accept.py",
    "tests/centurion/test_reservation_edit.py",
    "tests/centurion/test_reservation_register.py",
    "tests/centurion/test_reservation_search.py",
    # Ceramique
    "tests/home/test_landng_login.py",
    "tests/home/test_landng_nologin.py",
    "tests/home/test_language.py",
    "tests/home/test_membership.py",
    "tests/home/test_reservation.py"
]




# 테스트 실행
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
            duration=f"{duration:.2f}초"
        )

    except subprocess.CalledProcessError as e:
        duration = (datetime.now() - start_time).total_seconds()
        full_output = e.stderr or e.stdout or "출력 없음"

        # 전체 출력 라인으로 나눔
        error_lines = full_output.strip().splitlines()

        # 메시지 후보: 가장 마지막 줄 또는 AssertionError 등 포함된 줄
        parsed_message = ""
        for line in reversed(error_lines):
            if "Error" in line or "Exception" in line or "Traceback" in line or "Assertion" in line:
                parsed_message = line.strip()
                break

        # 예외가 없으면 마지막 줄 사용
        if not parsed_message and error_lines:
            parsed_message = error_lines[-1].strip()

        print(f"❌ {test_file} 테스트 실패")
        save_test_result(
            test_name=test_name,
            message=parsed_message,  # 깔끔한 에러 메시지만 저장
            status="FAIL",
            file_name=test_file,
            stack_trace=full_output,  # 전체는 stack_trace에 저장
            duration=f"{duration:.2f}초"
        )

print("\n🎯 모든 테스트 완료")

print("\n📤 슬랙 메시지 전송 중...")
subprocess.run(["python", "scripts/send_slack.py"])