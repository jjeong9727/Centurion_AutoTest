home_base_url = "https://stg.ceramiqueclinic.com/ko" #홈페이지 도메인
cen_base_url = "https://" #centurion 도메인

URLS = {
    "login_api" : "" , # API 호출 URL
    "home_main" : f"{home_base_url}",
    "home_login" : f"{home_base_url}/login",

    "home_discover" : f"{home_base_url}/discover",
    "home_removal" : f"{home_base_url}/removal/info",
    "home_lifting" : f"{home_base_url}/lifting/info",
    "home_privilege" : f"{home_base_url}/privilege",
    "home_discover" : f"{home_base_url}/discover",
    "home_mypage_pc" : f"{home_base_url}/my-page/membership",
    "home_mypage_mo" : f"{home_base_url}/m/my-page",
    "home_reservation" : f"{home_base_url}/",
    "cen_membership" : f"{cen_base_url}/",
    "cen_customer" :f"{cen_base_url}/customer",
    "cen_cust_register" :f"{cen_base_url}/customer/register",




    "footer_instagram" : "https://www.instagram.com/ceramique_clinic/", # 인스타그램 세라미크 계정 
    "kakaoch": "https://pf.kakao.com/_kzxmxfG", # 임시 URL 데이뷰  건대점
    "naverbk" : "https://booking.naver.com/booking/13/bizes/1048655" # 임시 URL 데이뷰 건대점
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
    },
    # 미성년자 정보
    "minor":{
        "name":"미성년자테스트",
        "birth" : "2008-08-08",
        "gender": "남자",
        "phone" : "010-0123-4567",
    }
}
