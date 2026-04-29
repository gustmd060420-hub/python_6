import os
import cv2
import numpy as np
from ultralytics import YOLO
from paddleocr import PaddleOCR
import re

print("🧠 [준비 중] YOLO 및 PaddleOCR 전문가를 불러옵니다...")
yolo_model = YOLO('best.pt')
ocr_model = PaddleOCR(lang='korean', use_angle_cls=True, show_log=False)

test_dir = 'combo_test_data'
total_images = 0
correct_predictions = 0

print("\n🚀 [콤보 모델 성능 평가 시작]")
print("-" * 50)

# 폴더 안의 모든 사진을 하나씩 꺼내서 채점
for filename in os.listdir(test_dir):
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')): 
        continue

    total_images += 1
    # 파일 이름에서 확장자를 뗀 부분 (이것이 진짜 정답!)
    true_label = os.path.splitext(filename)[0]

    # 사진 불러오기 (한글 경로 깨짐 방지)
    img_path = os.path.join(test_dir, filename)
    img_array = np.fromfile(img_path, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    # 1. YOLO로 번호판 찾기
    results = yolo_model(img, verbose=False)
    predicted_text = ""

    # 번호판을 찾았다면?
    if len(results[0].boxes) > 0:
        box = results[0].boxes[0].xyxy[0].cpu().numpy()
        x1, y1, x2, y2 = map(int, box)

        # 15픽셀 마법의 여백 주기
        pad = 15
        y1_p, y2_p = max(0, y1-pad), min(img.shape[0], y2+pad)
        x1_p, x2_p = max(0, x1-pad), min(img.shape[1], x2+pad)
        cropped = img[y1_p:y2_p, x1_p:x2_p]

        # 2. OCR로 글자 읽기
        ocr_res = ocr_model.ocr(cropped, cls=True)

        if ocr_res and ocr_res[0]:
            # X좌표 기준 정렬 및 특수문자 제거
            sorted_res = sorted(ocr_res[0], key=lambda x: x[0][0][0])
            raw_text = "".join([line[1][0] for line in sorted_res])
            clean_text = "".join(re.findall(r'[0-9가-힣]', raw_text))

            # 정규표현식으로 번호판 형식만 쏙 빼오기
            match = re.search(r'(\d{2,3}[가-힣]\d{4})', clean_text)
            if match:
                predicted_text = match.group(1)
            elif len(clean_text) >= 4:
                predicted_text = clean_text

    # 3. 채점하기
    if predicted_text == true_label:
        correct_predictions += 1
        print(f"✅ [정답] 파일: {true_label} ➡ 예측: {predicted_text}")
    else:
        print(f"❌ [오답] 파일: {true_label} ➡ 예측: {predicted_text}")

print("-" * 50)
if total_images > 0:
    accuracy = (correct_predictions / total_images) * 100
    print(f"📊 [최종 결과] 총 {total_images}장 중 {correct_predictions}장 정답! (정확도: {accuracy:.1f}%)")
else:
    print("⚠️ 폴더에 테스트할 사진이 없습니다!")