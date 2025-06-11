import os
from dotenv import load_dotenv


def login_with_token(page):
    load_dotenv()
    token = os.getenv("goole_access_token") # 구글 계정
    # token = os.getenv("kakao_access_token") # 카카오 계정
    key = os.getenv("storage_key")
    url = os.getenv("target_url")
    print(f" URL : {url}")

    page.goto(url)
    page.evaluate(f"""() => {{
        localStorage.setItem("{key}", "{token}");
    }}""")
    page.reload()
    page.wait_for_timeout(1000)
