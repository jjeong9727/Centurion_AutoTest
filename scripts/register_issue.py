import json
import os
import requests
import re
from urllib.parse import quote
from dotenv import load_dotenv

# .env 로드
load_dotenv()

# 환경 변수
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

HEADERS = {"Content-Type": "application/json"}
AUTH = (JIRA_EMAIL, JIRA_API_TOKEN)
def normalize_summary(name):
    name = re.sub(r"\[.*?\]", "", name)  # ✅ [자동화] 제거
    return re.sub(r"\s+", " ", name.strip())

def issue_exists(project_key, summary):
    safe_summary = normalize_summary(summary)
    jql = f'project = {project_key} AND summary ~ "{safe_summary}" ORDER BY created DESC'
    url = f"{JIRA_BASE_URL}/rest/api/2/search?jql={quote(jql)}"
    response = requests.get(url, headers=HEADERS, auth=AUTH)

    if response.status_code != 200:
        print(f"❌ 이슈 검색 실패: {response.status_code}, 응답: {response.text}")
        return None

    data = response.json()
    if data.get("total", 0) > 0:
        return data["issues"][0]["key"]  # 가장 최신 이슈의 키 반환
    return None

def create_issue(issue_data):
    url = f"{JIRA_BASE_URL}/rest/api/2/issue"
    payload = {
        "fields": {
            "project": {"key": issue_data["project"]},
            "summary": issue_data["summary"],
            "description": issue_data["description"],
            "issuetype": {"name": issue_data["issuetype"]},
            "priority": {"name": issue_data["priority"]},
            "labels": issue_data["labels"]
        }
    }

    response = requests.post(url, headers=HEADERS, auth=AUTH, json=payload)
    if response.status_code == 201:
        issue_key = response.json().get("key")
        print(f"✅ 이슈 등록 완료: {issue_key}")
        return issue_key
    else:
        print(f"❌ 이슈 등록 실패: {response.status_code} {response.text}")
        return None

def process_issues(json_path="scripts/jira_issues.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        issues = json.load(f)

    issue_map = {}

    for issue in issues:
        test_file = issue.get("file") or issue.get("summary")
        existing_key = issue_exists(issue["project"], issue["summary"])
        if existing_key:
            print(f"⚠️ 중복 이슈 존재: {issue['summary']} → {existing_key}")
            issue_map[test_file] = existing_key
        else:
            new_key = create_issue(issue)
            if new_key:
                issue_map[test_file] = new_key

    return issue_map

if __name__ == "__main__":
    keys = process_issues()
    print(f"📌 최종 이슈 목록: {keys}")