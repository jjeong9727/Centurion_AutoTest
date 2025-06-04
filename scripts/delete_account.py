# 홈페이지 계정 삭제 API 호출
# env 파일에 API URL, 계정 정보 저장됨 
import requests
import os
from dotenv import load_dotenv
from pathlib import Path

# 현재 파일(scripts/delete_account.py) 기준으로 tests/.env 경로 설정
env_path = Path(__file__).resolve().parents[1] / "tests" / ".env"
load_dotenv(dotenv_path=env_path)
# ✅ .env에서 API 주소와 이메일 목록 불러오기
API_BASE_URL = os.getenv("API_BASE_URL")
# EMAILS_TO_DELETE = os.getenv("EMAILS_TO_DELETE", "").split(",")
EMAILS_TO_DELETE = os.getenv("EMAILS_TO_DELETE", "").split(",")
BRANCH_ID = os.getenv("X_BRANCH_ID")

def delete_accounts():
    email_param = ",".join(EMAILS_TO_DELETE)
    url = f"{API_BASE_URL}?email={email_param}"
    headers = {
        "x-branch-id": BRANCH_ID
    }

    print(f"🔁 계정 삭제 요청 중")
    response = requests.delete(url, headers=headers)

    if response.status_code == 200:
        print("✅ 계정 삭제 요청 성공")
    else:
        print("❌ 삭제 요청 실패")
        print("상태 코드:", response.status_code)
        print("응답 내용:", response.text)

if __name__ == "__main__":
    delete_accounts()
