home_base_url = "https://stg.ceramiqueclinic.com/ko" #홈페이지 도메인
cen_base_url = "https://stg.centurion.ai.kr" #centurion 도메인

URLS = {
    # ==============HOME==============
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
    "home_complete" : f"{home_base_url}/complete",
    "home_mypage_profile": f"{home_base_url}/my-page/profile/edit",


    # ==============Centurion==============
    "cen_membership" : f"{cen_base_url}/",
    "cen_customer" :f"{cen_base_url}/",
    "cen_cust_detail" :f"{cen_base_url}/",
    "cen_login" : f"{cen_base_url}/login",
    "cen_main" : f"{cen_base_url}/reservations/management",



    # ==============외부 URL==============
    "footer_instagram" : "https://www.instagram.com/ceramique_clinic/", # 인스타그램 세라미크 계정 링크 
    "kakaoch": "https://pf.kakao.com/_kzxmxfG", # 카카오 상담 채널 링크
    "naver" : "https://booking.naver.com/booking/13/bizes/1048655" # 네이버 플레이스 링크
}

Account = {
    "testid" : "stg@medisolve.com",
    "testpw" : "12341234",
    "wrongpw" : "00000000"
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
