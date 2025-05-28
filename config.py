home_base_url = "https://" #홈페이지 도메인
cen_base_url = "https://" #centurion 도메인

URLS = {
    "login_api" : "" , # API 호출 URL
    "home_main" : f"{home_base_url}/main",
    "home_about" : f"{home_base_url}/about",
    "home_mypage" : f"{home_base_url}/",
    "home_reservation" : f"{home_base_url}/",
    "cen_membership" : f"{cen_base_url}/",
    "cen_customer" :f"{cen_base_url}/customer",
    "cen_cust_register" :f"{cen_base_url}/customer/register",




    "footer_instagram" : "https://www.instagram.com/daybeau_kd/", #임시 URL 데이뷰 건대점 
    "kakaoch": "https://pf.kakao.com/_kzxmxfG", # 임시 URL 데이뷰  건대점
    "naverbk" : "https://booking.naver.com/booking/13/bizes/1048655" # 임시 URL 데이뷰 건대점
}

Account={
    "testid" :"test1234",
    "testpw" :"test1234",
    "cust_name" : "" #고객명 
}


# 세라미크 예약 정보 

ReservationInfo = {
    # 예약자 정보
    "booker": {
        "name": "예약자테스트",
        "birth": "1990-09-09",
        "gender": "여자",
        "phone": "010-1234-5678",
    },
    # 방문자 정보
    "visitor": {
        "name": "방문자테스트",
        "birth": "1990-10-10",
        "gender": "남자",
        "phone": "010-9876-5432",
    }
}
