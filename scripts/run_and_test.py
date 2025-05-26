import json
import subprocess
from pathlib import Path
import requests
from datetime import datetime
import os
import platform

# ---------- 설정 ----------
DEVICE_FILE = Path("data/device_profile.json")
TESTS_DIR = Path("tests")
RESULT_JSON = Path("result.json")
JIRA_JSON = Path("jira_payload.json")
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/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" #Private
# SLACK_WEBHOOK_URL="https://hooks.slack.com/services/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" #채널

# ---------- 유틸: 테스트 실행 ----------
def run_pytest_with_device(name: str, profile: dict) -> dict:
    env = {
        "PLAYWRIGHT_VIEWPORT_WIDTH": str(profile['viewport']['width']),
        "PLAYWRIGHT_VIEWPORT_HEIGHT": str(profile['viewport']['height']),
        "PLAYWRIGHT_DEVICE_SCALE": str(profile['device_scale_factor']),
        "PLAYWRIGHT_IS_MOBILE": str(profile['is_mobile']),
        "PLAYWRIGHT_HAS_TOUCH": str(profile['has_touch']),
        "PLAYWRIGHT_USER_AGENT": profile['user_agent']
    }

    print(f"[RUNNING] {name} 환경에서 테스트 실행 중...")
    process = subprocess.run(
        ["pytest", str(TESTS_DIR), "--tb=short", "--maxfail=1"],
        capture_output=True,
        text=True,
        env={**env, **dict(os.environ)}
    )
    status = "success" if process.returncode == 0 else "failure"
    return {
        "device": name,
        "status": status,
        "stdout": process.stdout,
        "stderr": process.stderr
    }

# ---------- 유틸: Slack 전송 ----------
def send_slack_summary(summary: str):
    payload = { "text": summary }
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code != 200:
        print(f"[SLACK] 실패: {response.status_code} - {response.text}")
    else:
        print("[SLACK] 전송 완료")

# ---------- 파싱: 요약 및 실패 항목 -----------
def parse_failures_and_format_slack(result_json_path="result.json") -> tuple[str, list]:
    with open(result_json_path, encoding="utf-8") as f:
        results = json.load(f)

    pass_lines = []
    fail_lines = []
    failures = []
    os_info = platform.system() + platform.release()

    for result in results:
        device = result["device"]
        status = result["status"]
        test_file = extract_test_file_name(result["stdout"])

        line = f"- {os_info} | {test_file} {"PASS" if status == "success" else "FAIL"}"
        if status == "success":
            pass_lines.append(line)
        else:
            fail_lines.append(line)
            failures.append({
                "device": device,
                "error": extract_first_error_line(result["stderr"] or result["stdout"])
            })

    summary_text = (
        "세라미크 사전예약 테스트 결과\n"
        "테스트 정보 : 운영 서버 | PC / Mobile\n"
        "테스트 결과\n"
        + "\n".join(pass_lines + fail_lines)
    )

    return summary_text, failures

def extract_first_error_line(output: str) -> str:
    for line in output.splitlines():
        if "AssertionError" in line or "Error" in line:
            return line.strip()
    return output.strip().splitlines()[-1] if output else "Unknown error"

def extract_test_file_name(output: str) -> str:
    for line in output.splitlines():
        if "::" in line and ("PASSED" in line or "FAILED" in line):
            return line.split("::")[0].strip()
    return "알 수 없음"

# ---------- Jira 이슈용 포맷 ----------
def format_jira_issues(failures: list) -> list:
    issue_list = []
    for fail in failures:
        issue = {
            "summary": f"[{fail['device']}] {fail['error'][:100]}",
            "description": f"📱 *디바이스*: {fail['device']}\n\n🧪 *에러*: {fail['error']}",
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
        result = run_pytest_with_device(device_name, profile)
        results.append(result)

    # result.json 저장
    with open(RESULT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Slack & Jira 처리
    summary_text, failures = parse_failures_and_format_slack()
    send_slack_summary(summary_text)

    jira_issues = format_jira_issues(failures)
    with open(JIRA_JSON, "w", encoding="utf-8") as f:
        json.dump(jira_issues, f, ensure_ascii=False, indent=2)
    print("📁 jira_payload.json 파일 생성 완료")

if __name__ == "__main__":
    main()
