import pandas as pd
import json
from pathlib import Path

def generate_language_json(excel_path="data/language.xlsx", json_path="data/language.json"):
    df = pd.read_excel(excel_path)

    # 열 이름을 내부 처리용으로 변환
    df = df.rename(columns={
        "KEY": "key",
        "한국어": "ko",
        "영어": "en"
    })

    data = {}

    for _, row in df.iterrows():
        key = row["key"]
        data[key] = {
            "ko": row["ko"],
            "en": row["en"]
        }

    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] language.json 생성 완료 → {json_path}")

# 단독 실행 시
if __name__ == "__main__":
    generate_language_json()
