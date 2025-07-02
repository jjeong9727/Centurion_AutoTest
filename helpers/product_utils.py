from playwright.sync_api import Page, expect
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any
from helpers.product_utils import get_product_fields
from config import URLS

# 사용할 json 파일 리스트 
COUNT_FILE = Path("data/daily_count.json")
PRODUCT_FILE = Path("data/product.json")

# ✅검색 기능 확인 
def search_and_verify(
    page: Page,
    type_trigger_id: str = "",
    type_item_id: str = "",
    type_text: str = "",
    type_column_index: int = 0,
    search_field_id: str = "",
    search_value: str = "",
    table_selector: str = "table tbody tr",
    visible : bool = False
):
    # 초기 전체 행 개수 저장
    initial_count = page.locator(table_selector).count()
    print(f"📋 초기 행 개수: {initial_count}")

    # 유형 드롭다운 선택
    if type_trigger_id and type_item_id and type_text:
        print(f"🟢 유형 선택: {type_text}")
        page.click(f'[data-testid="{type_trigger_id}"]')
        page.wait_for_timeout(1000)
        page.locator(f'[data-testid="{type_item_id}"]', has_text=type_text).click()
        page.wait_for_timeout(2000)

        filtered_rows = page.locator(table_selector)
        count_after_type = filtered_rows.count()
        assert count_after_type > 0, f"❌ '{type_text}' 유형 선택 후 결과 없음"

        for i in range(count_after_type):
            row = filtered_rows.nth(i)
            
            if visible:
                toggle = row.locator("td").nth(4).locator("button[aria-label='노출']")
                assert toggle.is_visible(), f"❌ {i+1}번째 행의 노출 토글이 꺼져 있음"
            else:
                # ✅ 기본 텍스트 확인
                cell_text = row.locator("td").nth(type_column_index).inner_text()
                assert type_text in cell_text, f"❌ {i+1}번째 행의 {type_column_index+1}열에 '{type_text}' 없음"

        print(f"✅ 유형 '{type_text}' 선택 결과 검증 완료")


    # 검색어 입력
    if search_field_id and search_value:
        print(f"🔍 검색어 입력: {search_value}")
        page.fill(f'[data-testid="{search_field_id}"]', search_value)
        page.wait_for_timeout(500)
        page.locator("body").click(position={"x": 10, "y": 10})
        page.wait_for_timeout(2000)

    # 결과 행 개수 확인
    expected_result_count = 1
    final_rows = page.locator(table_selector)
    final_count = final_rows.count()
    assert final_count == expected_result_count, f"❌ 검색 결과: {final_count}건 (기대값: {expected_result_count})"
    print(f"✅ 검색 결과 {expected_result_count}건 확인 완료")

    # 초기화 버튼 클릭 후 행 개수 복원 확인
    print("♻️ 초기화 버튼 클릭")
    page.click(f'[data-testid="btn_reset"]')
    page.wait_for_timeout(1000)

    restored_count = page.locator(table_selector).count()
    assert restored_count == initial_count, f"❌ 초기화 후 행 개수 {restored_count} ≠ 초기 개수 {initial_count}"
    print(f"✅ 초기화 후 행 개수 복원 완료 ({restored_count}건)")


# ✅이탈 팝업 확인
def check_unsave_popup(page: Page):
    page.click('[data-testid="btn_back"]')
    page.wait_for_timeout(1000)
    expect(page.locator('[data-testid="txt_unsave"]')).to_have_text("변경사항을 저장하지 않으시겠습니까?", timeout=3000)
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_cancel"]')
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_back"]')
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_confirm"]')
    page.wait_for_timeout(1000)

# ✅수정 팝업 확인
def check_save_popup(
        page: Page, 
        popup_textid: str, 
        confirm_text: str, 
        toast_testid: str
):
    expect(page.locator(f'[data-testid="{popup_textid}"]')).to_have_text(confirm_text, timeout=3000)
    page.wait_for_timeout(500)
    page.locator('[data-testid="btn_confirm"]').click()
    page.wait_for_timeout(500)
    expect(page.locator(f'[data-testid="{toast_testid}"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

# ✅미노출/비활성화 변경 팝업 확인 
def switch_to_hidden(
    page: Page,
    toggle_testid: str,
    popup_textid: str,
    confirm_text: str,
    toast_testid: str
):
    #  토글 클릭 → "미노출/비활성화로 변경" 팝업 노출
    row = page.locator("table tbody tr").first
    row.locator(f'[data-testid="{toggle_testid}"]').click()
    page.wait_for_timeout(1000)
    expect(page.locator(f'[data-testid="{popup_textid}"]')).to_have_text(confirm_text, timeout=3000)
    page.wait_for_timeout(500)
    page.locator('[data-testid="btn_cancel"]').click()
    page.wait_for_timeout(1000)
    page.locator(f'[data-testid="{toggle_testid}"]').click()
    page.wait_for_timeout(1000)
    page.locator('[data-testid="btn_confirm"]').click()
    page.wait_for_timeout(500)
    #  토스트 메시지 확인
    expect(page.locator(f'[data-testid="{toast_testid}"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

# ✅노출/활성화 변경 팝업 확인 
def switch_to_visible(
    page: Page,
    toggle_testid: str,
    popup_textid: str,
    confirm_text: str,
    toast_testid: str
):
    #  토글 클릭 → "노출/활성화로 변경" 팝업 노출
    row = page.locator("table tbody tr").first
    row.locator(f'[data-testid="{toggle_testid}"]').click()
    page.wait_for_timeout(1000)
    expect(page.locator(f'[data-testid="{popup_textid}"]')).to_have_text(confirm_text, timeout=3000)
    page.wait_for_timeout(500)
    page.locator('[data-testid="btn_cancel"]').click()
    page.wait_for_timeout(1000)
    page.locator(f'[data-testid="{toggle_testid}"]').click()
    page.wait_for_timeout(1000)
    page.locator('[data-testid="btn_confirm"]').click()
    page.wait_for_timeout(500)
    #  토스트 메시지 확인
    expect(page.locator(f'[data-testid="{toast_testid}"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    
# ✅대분류 중분류 이름 생성
def generate_names(type: str) -> tuple[str, str]:
    type_map = {
        "대분류": "main",
        "중분류": "sub",
        "시술명": "treat",
        "상품명": "product",
        "페이지명": "title"
    }
    # 오늘 날짜 (MMDD 형식)
    today_key = datetime.now().strftime("%m%d")

    # 카운트 로드 또는 초기화
    if COUNT_FILE.exists():
        with open(COUNT_FILE, "r", encoding="utf-8") as f:
            count_data = json.load(f)
    else:
        count_data = {}

    # 카운트 증가
    count = count_data.get(today_key, 0) + 1
    count_data[today_key] = count

    # 카운트 저장
    with open(COUNT_FILE, "w", encoding="utf-8") as f:
        json.dump(count_data, f, ensure_ascii=False, indent=2)

    # 이름 구성
    name_ko = f"{type}_{today_key}_{count}"
    name_en = f"{type_map[type]}_{today_key}_{count}"

    return name_ko, name_en



# ✅product.json 업데이트 함수 (등록 수정 후 업데이트)
def update_product_fields(**kwargs: Any):
    """
    product.json의 항목을 선택적으로 업데이트합니다.
    사용 예:
        update_product_fields(new_main="대분류_0701_1", new_sub="중분류_0701_2")
    """

    if not PRODUCT_FILE.exists():
        raise FileNotFoundError(f"{PRODUCT_FILE} 파일이 존재하지 않습니다.")

    with open(PRODUCT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated = False
    for key, value in kwargs.items():
        if key in data:
            data[key] = value
            updated = True
        else:
            print(f"⚠️ 무시됨: '{key}'는 product.json에 존재하지 않는 키입니다.")

    if updated:
        with open(PRODUCT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 업데이트 완료: {', '.join(kwargs.keys())}")
    else:
        print("⚠️ 업데이트된 항목이 없습니다.")

# ✅product.json 불러오기 함수 (테스트 데이터 가져올때)
def get_product_fields(*keys: str) -> dict[str, Any]:
    """
    product.json에서 지정된 키만 선택적으로 불러옵니다.
    사용 예:
        get_product_fields("main", "new_main")
    반환 예:
        {"main": "대분류수정테스트", "new_main": "대분류_0701_1"}
    """

    if not PRODUCT_FILE.exists():
        raise FileNotFoundError(f"{PRODUCT_FILE} 파일이 존재하지 않습니다.")

    with open(PRODUCT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = {}
    for key in keys:
        if key in data:
            result[key] = data[key]
        else:
            print(f"⚠️ '{key}'는 product.json에 존재하지 않습니다. 무시됩니다.")

    return result

# ✅Centurion 내 화면에서 확인 하는 공통 함수 
def verify_dropdown_values(
    page: Page,
    page_url: str,
    field_pairs: list[tuple[str, str]],  # ex) [("main", "new_main"), ("sub", "new_sub")]
    testid_map: dict[str, str]          # ex) {"trigger": "drop_ctg_main_trigger", "search": "drop_ctg_main_search", "item": "drop_ctg_main_item"}
):
    # ✅ 진입
    page.goto(page_url)
    page.wait_for_timeout(1000)

    # ✅ product.json에서 필요한 값만 가져오기
    keys_to_fetch = list({k for pair in field_pairs for k in pair})
    product_data = get_product_fields(*keys_to_fetch)

    # ✅ 각 항목 확인
    for old_key, new_key in field_pairs:
        old_val = product_data.get(old_key)
        new_val = product_data.get(new_key)

        if old_val:
            print(f"🔍 '{old_val}' 항목이 미노출 상태인지 확인 중...")
            # 드롭다운 열기
            page.click(f'[data-testid="{testid_map["trigger"]}"]')
            page.wait_for_timeout(1000)

            # 검색
            page.fill(f'[data-testid="{testid_map["search"]}"]', old_val)
            page.wait_for_timeout(1000)

            # 미노출 확인 (없어야 함)
            expect(page.locator(f'[data-testid="{testid_map["item"]}"]').first).not_to_have_text(old_val)

            # 검색창 초기화
            page.locator("body").click(position={"x": 10, "y": 10})
            page.wait_for_timeout(1000)

        if new_val:
            print(f"🔍 '{new_val}' 항목이 노출 상태인지 확인 중...")
            # 드롭다운 열기
            page.click(f'[data-testid="{testid_map["trigger"]}"]')
            page.wait_for_timeout(1000)

            # 검색
            page.fill(f'[data-testid="{testid_map["search"]}"]', new_val)
            page.wait_for_timeout(1000)

            # 노출 확인 (있어야 함)
            expect(page.locator(f'[data-testid="{testid_map["item"]}"]').first).to_have_text(new_val)

            # 검색창 초기화
            page.locator("body").click(position={"x": 10, "y": 10})
            page.wait_for_timeout(1000)


# 설명 생성 함수 
def generate_random_korean_text(length=20):
    words = ["인중", "앞턱", "아랫턱", "이마", "볼", "광대", "코", "입술", "목", "턱선", "귀밑", "눈밑", "팔자", "옆볼"]
    return " + ".join(random.sample(words, k=min(len(words), length)))[:length]
def generate_random_english_text(length=20):
    words = ["chin", "forehead", "jaw", "cheek", "nose", "neck", "temple", "lip", "underchin", "earline", "eye", "smileline"]
    return " + ".join(random.sample(words, k=min(len(words), length)))[:length]
def generate_random_sub_description(lang="ko"):
    if lang == "ko":
        return "**장비 택1 / 마취크림, 진정크림 포함"
    else:
        device = random.choice(["1 device", "laser", "ultrasound", "RF"])
        anesthetic = random.choice(["anesthetic", "numbing cream"])
        calming = random.choice(["calming cream", "soothing gel", "repair mask"])
        return f"**{device} / includes {anesthetic} & {calming}"
def generate_random_description(lang="ko"):
    if lang =="ko":
        message_ko = (
            "※ 시술 전후 피부 상태에 따라 결과는 개인차가 있을 수 있습니다.\n"
            "시술 전 반드시 전문의와 상담해 주세요.\n"
            "최근 2주 내 레이저·필링 치료 이력이 있다면 미리 알려주세요.\n"
            "📅 유효기간: 2025.07.01 ~ 2025.09.30\n"
            "💳 카드/현금/모바일결제 가능\n"
            "☎️ 문의: 010-1234-5678\n"
            "* 본 시술은 미성년자에게 제공되지 않습니다."
        )
        return message_ko
    else:
        message_en = (
            "* Results may vary depending on skin condition before/after treatment.\n"
            "Please consult with a dermatologist before the procedure.\n"
            "Let us know if you had laser/peeling treatment in the past 2 weeks.\n"
            "📅 Valid: 2025.07.01 ~ 2025.09.30\n"
            "💳 Card/Cash/Mobile payment accepted\n"
            "☎️ Contact: 010-1234-5678\n"
            "* This procedure is not available for minors."
        )
        return message_en
def generate_descriptions():
    return {
        "main_ko": generate_random_korean_text(),
        "main_en": generate_random_english_text(),
        "sub_ko": generate_random_sub_description("ko"),
        "sub_en": generate_random_sub_description("en"),
        "des_ko" : generate_random_description("ko"),
        "des_en" : generate_random_description("en")
    }

# 이미지 등록 유효성 확인 
def check_invalid_upload(page: Page, file_path: str, toast_testid: str):
    upload_locator = page.locator('[data-testid="upload_image"]')
    upload_locator.wait_for(state="attached", timeout=5000)
    element = upload_locator.element_handle()
    assert element is not None, "❌ 파일 업로드 input 요소를 찾을 수 없습니다."
    element.set_input_files(file_path)
    page.wait_for_timeout(5000)
    expect(page.locator(f'[data-testid="{toast_testid}"]')).to_be_visible(timeout=3000)
    print(f"✅ {toast_testid} 토스트 확인 완료")

# 이미지 등록 함수
def upload_image(page:Page, file_path:str, image_name:str):
    upload_locator = page.locator('[data-testid="upload_image"]')
    upload_locator.wait_for(state="attached", timeout=5000)
    element = upload_locator.element_handle()
    assert element is not None, "❌ 파일 업로드 input 요소를 찾을 수 없습니다."
    element.set_input_files(file_path)
    page.wait_for_timeout(5000)
    expect(page.locator('[data-testid="txt_image"]')).to_have_text(image_name)
    page.wait_for_timeout(1000)
    

# 상품 가격 생성
def generate_price_info():
    times = random.choice([5, 10]) # 횟수 5 or 10
    price = random.choice([i * 100000 for i in range(1, 6)]) # 정가: 100,000 ~ 500,000 중 십만원 단위
    discount_candidates = [
        p for p in range(10000, price, 1000) if str(p).endswith("900") # 할인가: 900원으로 끝나는 값
    ]
    discount = random.choice(discount_candidates)
    rate = int((price - discount) * 100 / price) # 할인율: (정가 - 할인가) / 정가 * 100 (→ 정수)

    return {
        "times": str(times),
        "price": str(price),
        "discount": str(discount),
        "rate": str(rate)
    }

# 상품 가격 입력 함수
def fill_group_price_info(page, group_id: int, price_info: dict):
    group_locator = page.locator(f'[data-testid="group{group_id}"]')

    group_locator.locator('[data-testid="input_times"]').fill(price_info["times"])
    page.wait_for_timeout(500)

    group_locator.locator('[data-testid="input_price"]').fill(price_info["price"])
    page.wait_for_timeout(500)

    group_locator.locator('[data-testid="input_discount"]').fill(price_info["discount"])
    page.wait_for_timeout(500)

    group_locator.locator('[data-testid="input_rate"]').fill(price_info["rate"])
    page.wait_for_timeout(500)

# 상품 관리 / 상품 페이지 관리 > 시술 / 컨텐츠 삭제 플로우
def delete_all_items(page: Page, delete_btn_testid: str):
    """
    반복 가능한 삭제 버튼을 찾아 모두 클릭.
    버튼이 하나도 안 남으면 종료됨.
    """
    while True:
        delete_buttons = page.locator(f'[data-testid="{delete_btn_testid}"]')
        if delete_buttons.count() == 0:
            print(f"✅ '{delete_btn_testid}' 항목 모두 삭제 완료")
            break

        delete_buttons.first.click()
        page.wait_for_timeout(1000)



# 🚫 홈페이지 추후 구성 필요 
# # 홈페이지 반영 확인 
# def check_category_menu(page: Page, expected: dict):
#     field = get_product_fields("new_main", "new_sub", "new_treat", "new_product", "new_title")
#     main = field["new_main"]
#     sub = field["new_sub"]
#     title = field["new_title"]
#     product = field["new_product"]

#     page.goto(URLS["home_product"])
#     page.wait_for_timeout(3000)
#     expect(page.locator('[data-testid="page_title"]')).to_have_text("제모 시술 가격 안내")
#     page.wait_for_timeout(500)
#     page.locator('[data-testid="category_main"]', has_text=main).click
#     page.wait_for_timeout(500)
#     page.locator('[data-testid="category_sub"]', has_text=sub).click
#     page.wait_for_timeout(500)
#     expect(page.locator('[data-testid="page_name"]')).to_have_text(title)




    	
