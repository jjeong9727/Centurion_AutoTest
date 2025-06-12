import os
from dotenv import load_dotenv


def login_with_token(page, account_type="google"):
    from dotenv import load_dotenv
    import os

    load_dotenv()

    google_token = os.getenv("google_access_token")
    kakao_token = os.getenv("kakao_access_token")
    key = os.getenv("storage_key")
    url = os.getenv("target_url")

    # 계정 타입에 따른 토큰 선택
    if account_type == "google":
        token = google_token
    elif account_type == "kakao":
        token = kakao_token
    else:
        raise ValueError(f"지원하지 않는 계정 타입: {account_type}")

    # 로그인 흐름
    page.goto(url)
    page.evaluate(f"""() => {{
        localStorage.setItem("{key}", "{token}");
    }}""")
    page.reload()
    page.wait_for_timeout(3000)
