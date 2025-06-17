home_base_url = "https://stg.ceramiqueclinic.com" #홈페이지 도메인
cen_base_url = "https://stg.centurion.ai.kr" #centurion 도메인

URLS = {
    # ==============HOME==============
    "home_main" : f"{home_base_url}",
    "home_login" : f"{home_base_url}/login",
    "home_discover" : f"{home_base_url}/discover",
    "home_removal" : f"{home_base_url}/removal/info",
    "home_lifting" : f"{home_base_url}/lifting/info",
    "home_privacy" : f"{home_base_url}/privacy",
    "home_terms" : f"{home_base_url}/terms",
    "home_privilege" : f"{home_base_url}/privilege",
    "home_discover" : f"{home_base_url}/discover",
    "home_mypage_mem" : f"{home_base_url}/my-page/membership",
    "home_mypage_profile" : f"{home_base_url}/my-page/profile/edit",
    "home_mypage_history" : f"{home_base_url}/my-page/reservations",
    "home_mypage_mo" : f"{home_base_url}/my-page",
    "home_reservation" : f"{home_base_url}/reservation",
    "home_complete" : f"{home_base_url}/complete",
    "home_mypage_profile": f"{home_base_url}/my-page/profile/edit",




    # ==============Centurion==============
    "cen_membership" : f"{cen_base_url}/customers/memberships/grades",
    "cen_customer" :f"{cen_base_url}/customers/management",
    "cen_login" : f"{cen_base_url}/login",
    "cen_main" : f"{cen_base_url}/reservations/management",
    "cen_reservation" : f"{cen_base_url}/reservations/management",
    "cen_grade" : f"{cen_base_url}/customers/memberships/grades",
    "cen_record" : f"{cen_base_url}/recordings/management",



    # ==============외부 URL==============
    "footer_instagram" : "https://www.instagram.com/ceramique_clinic/", # 인스타그램 세라미크 계정 링크 
    "naver" : "https://booking.naver.com/booking/13/bizes/1048655", # 네이버 플레이스 링크
    "whatsapp" : "https://api.whatsapp.com/send/?phone=821076094217&text&type=phone_number&app_absent=0" #왓츠앱 앱 설치 링크 
}

Account = {
    "testid" : "stg@medisolveai.com",
    "testpw" : "12341234",
    "wrongpw" : "00000000"
}

# 세라미크 예약 정보 
ReservationInfo = {
    # 예약자 정보
    "booker": {
        "name": "자동화한국인",
        "birth": "1997-09-27",
        "gender": "여성",
        "phone": "010-6275-4153",
    },
    # 방문자 정보
    "visitor": {
        "name": "방문자테스트",
        "birth": "1990-10-10",
        "gender": "여성",
        "phone": "010-9876-5432",
    },
    # 미성년자 정보
    "minor":{
        "name":"미성년자테스트",
        "birth" : "2008-08-08",
        "gender": "여성",
        "phone" : "010-0123-4567",
    }
}

# 세라미크 랜딩 확인용 매핑 
MENU_META_nologin = {
    "discover": {
        "testid": "menu_discover",
        "path": "/discover"
    },
    "removal": {
        "testid": "menu_removal",
        "path": "/removal/info"
    },
    "lifting": {
        "testid": "menu_lifting",
        "path": "/lifting/info"
    },
    "privilege": {
        "testid": "menu_privilege",
        "path": "/events/privilege"
    },
    "login": {
        "testid": "menu_login",
        "path": "/login"
    }
}
MENU_META_login = {
    "discover": {
        "testid": "menu_discover",
        "path": "/discover"
    },
    "removal": {
        "testid": "menu_removal",
        "path": "/removal/info"
    },
    "lifting": {
        "testid": "menu_lifting",
        "path": "/lifting/info"
    },
    "privilege": {
        "testid": "menu_privilege",
        "path": "/events/privilege"
    },
    "mypage": {
        "testid": "menu_mypage",
        "path": "/my-page"
    },
    "logout":{
        "testid" : "menu_logout",
        "path" : ""
    }
}