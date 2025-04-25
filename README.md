# Home_AutoTest
>사용 Tool : Python + Playwright

##테스트 파일 구조##
1. Root
  - 최상단 폴더
>config.py
> - 공통 변수 저장 파일
> - URL, Account 등등


2. data 폴더
  - 테스트에서 사용하는 데이터 파일들을 보관하는 폴더
>language.xlsx
>- 다국어 매핑 정보가 저장된 엑셀 파일
>- 유지보수를 위해 엑셀에서 관리, 이후 json에 저장하여 테스트에 활용

>language.json 
>- 다국어 매핑 되어있는 엑셀 파일에서 생성된 값
>- 자동화 테스트에 사용되는 실 데이터 값 

>device_profile.json 
>- 모바일 테스트 대상 단말 정보
>- 해상도, 브라우저 정보 등 


3. helpers 폴더
  - 테스트를 도와주는 공통 기능(유틸리티) 코드들이 들어 있는 폴더


4. scripts 폴더
  - 데이터 가공이나 사전 준비 or 테스트 이후 작업을 위한 실행용 스크립트 파일
> language_mapping.py 
>- 다국어 매핑 정보 엑셀 → json 파일로 변환하는 파일


5. tests 폴더
  - 실제 자동화 테스트 케이스들이 저장되는 핵심 폴더
>conftest.py
>- 웹/모바일 테스트 설정 및 브라우저 지정
>- 테스트 파일 모두에 영향을 줌
>- 테스트 파일 실행 시 웹 / Android / iOS 모두 실행 되는 형태

>test_home_ui.py
>- 홈페이지 진입 및 UI 요소 확인 스크립트

