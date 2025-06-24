# helpers/image_assets.py
from pathlib import Path

FIXTURE_DIR = Path(__file__).resolve().parent.parent / "data" / "fixtures"

# 이벤트 등록용 이미지
event_img     = str(FIXTURE_DIR / "img_event.jpg")
detail_img_1  = str(FIXTURE_DIR / "img_event_1.jpg")
detail_img_2  = str(FIXTURE_DIR / "img_event_2.png")
detail_img_3  = str(FIXTURE_DIR / "img_event_3.png")
detail_img_4  = str(FIXTURE_DIR / "img_event_4.jpg")
detail_img_5  = str(FIXTURE_DIR / "img_event_5.jpg")
detail_img_6  = str(FIXTURE_DIR / "img_event_6.png")
popup_img     = str(FIXTURE_DIR / "img_popup.jpg")

# 이벤트 수정용 이미지
edit_img      = str(FIXTURE_DIR / "img_edit_event.png")
edit_detail   = str(FIXTURE_DIR / "img_edit_detail.png")
edit_popup    = str(FIXTURE_DIR / "img_edit_popup.jpg")

# 이미지 등록 유효성 확인용
overspec_img  = str(FIXTURE_DIR / "img_overspec.jpg")
nonspec_img   = str(FIXTURE_DIR / "img_nonspec.gif")
nonspec_video = str(FIXTURE_DIR / "video.mp4")
