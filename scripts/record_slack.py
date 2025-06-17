import os
import requests
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
if not SLACK_WEBHOOK_URL:
    raise ValueError("❌ SLACK_WEBHOOK_URL 환경변수가 설정되어 있지 않습니다.")

def send_custom_slack_message(pass_items=None, fail_items=None, fail_reason=None):
    pass_items = pass_items or []
    fail_items = fail_items or []

    lines = [":mega: [Centurion] 녹취 자동화 테스트 결과 공유"]

    for item in pass_items:
        lines.append(f"{item} ✅ PASS")

    for item in fail_items:
        lines.append(f"{item} ❌ *FAIL*")

    if fail_reason:
        lines.append(f"\n🔴 실패 원인: {fail_reason}")

    payload = {
        "text": "\n".join(lines)  # 👈 일반 메시지 형식
    }

    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code != 200:
        raise Exception(f"Slack 전송 실패: {response.status_code} {response.text}")
