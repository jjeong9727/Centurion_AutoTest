import os
import json
import time
import requests
from config import URLS, Account

TOKEN_FILE = "state/login_token.json"

def get_login_token():
    """백엔드 API 호출해서 access_token 얻기"""
    url = URLS["login_api"]
    payload = {
        "id": Account["testid"],
        "password": Account["testpw"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    token_info = response.json()
    return {
        "access_token": token_info["access_token"],
        "expires_at": int(time.time()) + token_info.get("expires_in", 3600)  # 만료시간 계산
    }

def save_token_to_file(token_data):
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(token_data, f, indent=2)

def load_token_from_file():
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def ensure_valid_token():
    """토큰 파일을 확인하고, 없거나 만료되었으면 새로 발급"""
    token_data = load_token_from_file()

    if token_data and token_data["expires_at"] > int(time.time()):
        # 아직 유효한 토큰
        print("✅ 유효한 토큰을 불러왔습니다.")
        return token_data["access_token"]

    print("⚠️ 토큰이 없거나 만료되었습니다. 새로 발급합니다.")
    new_token = get_login_token()
    save_token_to_file(new_token)
    return new_token["access_token"]
