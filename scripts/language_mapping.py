import pandas as pd
import json
from pathlib import Path

def generate_language_json(excel_path="data/language.xlsx", json_path="data/language.json"):
    df = pd.read_excel(excel_path)

    # 열 이름을 내부 처리용으로 변환
    df = df.rename(columns={
        "화면": "screen",    # screen 열이 "화면"이라는 이름으로 저장된 경우
        "KEY": "key",
        "한국어": "ko",
        "영어": "en"
    })

    data = {}

    for _, row in df.iterrows():
        screen = row["screen"]
        key = row["key"]
        ko = row["ko"]
        en = row["en"]

        if screen not in data:
            data[screen] = {}

        data[screen][key] = {
            "ko": ko,
            "en": en
        }

    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] language.json 생성 완료 → {json_path}")

# 단독 실행 시
if __name__ == "__main__":
    generate_language_json()