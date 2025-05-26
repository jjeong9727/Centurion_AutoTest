# home_base_url = "https://www.gangnam.ceramiqueclinic.com/ko/pre-booking" #홈페이지 도메인
home_base_url = "https://stg.ceramiqueclinic.com/ko/pre-booking" #홈페이지 STG
#cen_base_url = "https://" #centurion 도메인

URLS = {
#    "login_api" : "" , # API 호출 URL
    "home_main" : f"{home_base_url}",
#    "home_about" : f"{home_base_url}/about",
#    "home_mypage" : f"{home_base_url}/",
    "home_reservation" : f"{home_base_url}/create",
    "home_privacy" : f"https://stg.ceramiqueclinic.com/ko/privacy",
    "home_terms" : f"https://stg.ceramiqueclinic.com/ko/terms",
    "home_reservation_complete" : f"{home_base_url}/complete",
#    "cen_membership" : f"{cen_base_url}/",
#    "cen_customer" :f"{cen_base_url}/customer",
#    "cen_cust_register" :f"{cen_base_url}/customer/register",




    "footer_instagram" : "https://www.instagram.com/ceramique_clinic/#", #세라미크 인스타 
#    "kakaoch": "https://pf.kakao.com/_kzxmxfG", # 임시 URL 데이뷰  건대점
#    "naverbk" : "https://booking.naver.com/booking/13/bizes/1048655" # 임시 URL 데이뷰 건대점
}

#Account={
#    "testid" :"test1234",
#    "testpw" :"test1234",
#    "cust_name" : "" #고객명 
#}