import os
import cv2
import numpy as np
from ultralytics import YOLO
from paddleocr import PaddleOCR
import re

# 💡 [핵심 추가] 번호판 문법 검사 및 자동 교정기
def correct_plate_format(text):
    # 1. 특수문자 및 띄어쓰기 싹 다 제거 (숫자와 한글만 남김)
    clean_text = re.sub(r'[^0-9가-힣]', '', text)
    
    # 2. 이미 완벽한 형식이면 그대로 통과
    match = re.search(r'(\d{2,3}[가-힣]\d{4})', clean_text)
    if match:
        return match.group(1)
        
    # 3. AI가 한글을 숫자로 착각했을 때의 자동 복구 사전
    # (모양 때문에 자주 헷갈리는 글자들을 등록해 둡니다)
    correction_map = {'4': '나', '0': '어', '1': '너', '2': '러', '5': '도', '8': '가', '3': '다'}
    
    # 8자리 번호판 (예: 123가4567)인데 4번째가 숫자인 경우 (예: 28144517)
    if len(clean_text) == 8 and clean_text[:3].isdigit() and clean_text[4:].isdigit():
        wrong_char = clean_text[3]
        if wrong_char in correction_map:
            return clean_text[:3] + correction_map[wrong_char] + clean_text[4:]
            
    # 7자리 번호판 (예: 12가3456)인데 3번째가 숫자인 경우
    elif len(clean_text) == 7 and clean_text[:2].isdigit() and clean_text[3:].isdigit():
        wrong_char = clean_text[2]
        if wrong_char in correction_map:
            return clean_text[:2] + correction_map[wrong_char] + clean_text[3:]

    # 복구가 불가능하면 일단 정제된 텍스트 반환
    return clean_text


print("🧠 [준비 중] YOLO 및 PaddleOCR 전문가를 불러옵니다...")
yolo_model = YOLO('best.pt')
ocr_model = PaddleOCR(lang='korean', use_angle_cls=True, show_log=False)

test_dir = 'combo_test_data'
total_images = 0
correct_predictions = 0

print("\n🚀 [콤보 모델 성능 평가 시작 (V2: 확장 여백 + 문법 교정)]")
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

        # 1. 과유불급! 여백을 노이즈가 없는 '황금 비율'로 줄입니다.
        box_width = x2 - x1
        box_height = y2 - y1
        
        pad_x = int(box_width * 0.08)  # 15% ➡ 8%로 축소 (옆면 범퍼 안 잡히게)
        pad_y = int(box_height * 0.05) # 15% ➡ 5%로 축소 (위아래 테두리 안 잡히게)
        
        y1_p, y2_p = max(0, y1 - pad_y), min(img.shape[0], y2 + pad_y)
        x1_p, x2_p = max(0, x1 - pad_x), min(img.shape[1], x2 + pad_x)
        cropped = img[y1_p:y2_p, x1_p:x2_p]

        # 💡 [새로운 특급 비법] 자른 번호판 사진을 강제로 2배 확대시킵니다!
        # (작고 뭉개진 글자도 OCR이 아주 선명하게 읽을 수 있게 됩니다.)
        cropped = cv2.resize(cropped, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)

        # 2. 확대된 고화질 사진으로 OCR 글자 읽기
        ocr_res = ocr_model.ocr(cropped, cls=True)

        if ocr_res and ocr_res[0]:
            # X좌표 기준 정렬
            sorted_res = sorted(ocr_res[0], key=lambda x: x[0][0][0])
            raw_text = "".join([line[1][0] for line in sorted_res])
            
            # 💡 [핵심 수정 2] 문법 검사기로 후처리 진행
            predicted_text = correct_plate_format(raw_text)

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