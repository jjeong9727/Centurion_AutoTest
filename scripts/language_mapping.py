import pandas as pd
import json
from pathlib import Path

def generate_language_json(excel_path="language.xlsx", json_path="json/language.json"):
    df = pd.read_excel(excel_path)
    data = {}

    for _, row in df.iterrows():
        key = row["key"]
        data[key] = {
            "ko": row["ko"],
            "en": row["en"],
            "ja": row["ja"],
            "ch": row["zh-cn"],
            "th": row["th"],
            "vi": row["vi"]
        }

    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] language.json 생성 완료 → {json_path}")

# 단독 실행 시 바로 생성
if __name__ == "__main__":
    generate_language_json()
