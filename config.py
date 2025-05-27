import os

is_mobile = os.getenv("PLAYWRIGHT_IS_MOBILE", "false").lower() == "true"

home_base_url = "https://www.gangnam.ceramiqueclinic.com/ko/pre-booking" #PRD
home_base_url_mw = "https://www.gangnam.ceramiqueclinic.com/ko/m/pre-booking" #PRD


# home_base_url = "https://stg.ceramiqueclinic.com/ko/pre-booking" # STG
# home_base_url_mw = "https://stg.ceramiqueclinic.com/ko/m/pre-booking" # STG
BASE = home_base_url_mw if is_mobile else home_base_url

URLS = {
    "home_main": BASE,
    "home_reservation": f"{BASE}/create",
    "home_reservation_complete": f"{BASE}/complete",
    "home_privacy": BASE.replace("/pre-booking", "/privacy"),
}

