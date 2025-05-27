import json
import subprocess
from pathlib import Path
import requests
from datetime import datetime
import os
import platform
from collections import defaultdict
from dotenv import load_dotenv


# ---------- 설정 ----------
DEVICE_FILE = Path("data/device_profile.json")
TESTS_DIR = Path("tests")
RESULT_JSON = Path("result.json")
JIRA_JSON = Path("jira_payload.json")
load_dotenv()
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# 테스트 파일명을 한글로 매핑
TEST_NAME_KR = {
    "test_landing.py": "화면 진입 테스트",
    "test_language.py": "언어 변환 테스트",
    "test_pre-reserve.py": "예약 신청 테스트"
}

# ---------- 유틸: 테스트 실행 ----------
def run_pytest_with_device(name: str, profile: dict) -> list:
    is_mobile = profile["is_mobile"]
    base_url = "https://www.gangnam.ceramiqueclinic.com/ko/m/pre-booking" if is_mobile else "https://www.gangnam.ceramiqueclinic.com/ko/pre-booking"

    env = {
        "PLAYWRIGHT_VIEWPORT_WIDTH": str(profile['viewport']['width']),
        "PLAYWRIGHT_VIEWPORT_HEIGHT": str(profile['viewport']['height']),
        "PLAYWRIGHT_DEVICE_SCALE": str(profile['device_scale_factor']),
        "PLAYWRIGHT_IS_MOBILE": str(profile['is_mobile']),
        "PLAYWRIGHT_HAS_TOUCH": str(profile['has_touch']),
        "PLAYWRIGHT_USER_AGENT": profile['user_agent'],
        "PLAYWRIGHT_TEST_BASE_URL": base_url
    }

    test_files = [
        "test_landing.py",
        "test_language.py"
    ]
    if not is_mobile:
        test_files.append("test_pre-reserve.py")

    results = []
    for test_file in test_files:
        print(f"[RUNNING] {name} 환경에서 {test_file} 실행 중...")
        process = subprocess.run(
            ["pytest", str(TESTS_DIR / test_file), "--tb=short", "--maxfail=1"],
            capture_output=True,
            text=True,
            env={**env, **dict(os.environ)}
        )
        status = "success" if process.returncode == 0 else "failure"
        results.append({
            "device": name,
            "test_file": test_file,
            "status": status,
            "stdout": process.stdout,
            "stderr": process.stderr
        })
    return results

# ---------- 유틸: Slack 전송 ----------
def send_slack_summary(summary: str):
    payload = { "text": summary }
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code != 200:
        print(f"[SLACK] 실패: {response.status_code} - {response.text}")
    else:
        print("[SLACK] 전송 완료")

def extract_test_file_name(output: str) -> str:
    for line in output.splitlines():
        if "::" in line and ("PASSED" in line or "FAILED" in line):
            file_name = line.split("::")[0].strip().split("/")[-1]
            return TEST_NAME_KR.get(file_name, file_name)  # ⬅ 매핑 실패 시 원본 사용
    return "알 수 없음"



# ---------- 파싱: 요약 및 실패 항목 -----------
from collections import defaultdict

def parse_failures_and_format_slack(result_json_path="result.json") -> tuple[str, list]:
    with open(result_json_path, encoding="utf-8") as f:
        results = json.load(f)

    os_info = platform.system() + platform.release()
    grouped_results = defaultdict(list)
    device_order = []

    # ✅ 장치별로 그룹핑
    for result in results:
        device = result["device"]
        if device not in device_order:
            device_order.append(device)
        grouped_results[device].append(result)

    lines = []
    failures = []

    for device in device_order:
        for result in grouped_results[device]:
            test_file = result.get("test_file", "알 수 없음")
            test_name = TEST_NAME_KR.get(test_file, test_file)
            status = result["status"]

            line = f"- {device} | {test_name} {'PASS' if status == 'success' else 'FAIL'}"
            lines.append(line)

            if status != "success":
                failures.append({
                    "device": device,
                    "test_file": test_file,
                    "error": extract_first_error_line(result["stderr"] or result["stdout"])
                })

    summary_text = (
        "세라미크 사전예약 테스트 결과\n"
        "테스트 정보 : PRD Server | PC / Mobile\n"
        "테스트 결과\n"
        + "\n".join(lines)
    )

    return summary_text, failures




def extract_first_error_line(output: str) -> str:
    for line in output.splitlines():
        if "AssertionError" in line or "Error" in line:
            return line.strip()
    return output.strip().splitlines()[-1] if output else "Unknown error"

# ---------- Jira 이슈용 포맷 ----------
def format_jira_issues(failures: list) -> list:
    issue_list = []
    for fail in failures:
        test_file = fail.get("test_file", "")
        test_kr_name = TEST_NAME_KR.get(test_file, test_file)

        issue = {
            "summary": f"[{fail['device']}] {test_kr_name} 실패 - {fail['error'][:60]}",
            "description": f"📱 *디바이스*: {fail['device']}\n🧪 *에러*: {fail['error']}",
            "project": "QA",
            "issuetype": "Bug",
            "priority": "Medium",
            "labels": ["playwright", "automated-test"]
        }
        issue_list.append(issue)
    return issue_list

# ---------- 메인 실행 ----------
def main():
    if not DEVICE_FILE.exists():
        print("[ERROR] device_profile.json 파일이 없습니다.")
        return

    with open(DEVICE_FILE, encoding="utf-8") as f:
        devices = json.load(f)

    results = []
    for device_name, profile in devices.items():
        device_results = run_pytest_with_device(device_name, profile)
        results.extend(device_results)

    with open(RESULT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    summary_text, failures = parse_failures_and_format_slack()
    send_slack_summary(summary_text)

    jira_issues = format_jira_issues(failures)
    with open(JIRA_JSON, "w", encoding="utf-8") as f:
        json.dump(jira_issues, f, ensure_ascii=False, indent=2)
    print("📁 jira_payload.json 파일 생성 완료")

if __name__ == "__main__":
    main()