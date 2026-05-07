import cv2
from ultralytics import YOLO
from paddleocr import PaddleOCR
import matplotlib.pyplot as plt
import re
import os

# 한글 폰트 깨짐 방지
plt.rc('font', family='Malgun Gothic')

print("🤖 [1단계] AI 전문가들을 소집하는 중입니다...")
# 1. 내가 학습시킨 YOLO 전문가 모델 불러오기
yolo_model = YOLO('best.pt') 
# 2. 글자 읽기 전문가 PaddleOCR 불러오기
ocr_model = PaddleOCR(use_angle_cls=True, lang='korean', show_log=False)

# 테스트할 이미지 1장 선택 (ocr_test_data 폴더 안의 사진 중 하나를 고르세요)
# ocr_test_data 폴더 말고, 자동차 전체가 있는 원본 사진으로 테스트!
img_path = 'images_car1.jpg' 

# 💡 여기서 괄호 안의 변수를 img_path로 바꿔줍니다!
print(f"\n📸 [2단계] '{img_path}' 사진 분석을 시작합니다.")
img = cv2.imread(img_path)

# 1. YOLO에게 번호판 위치 찾으라고 명령!
results = yolo_model(img)

# 번호판을 성공적으로 찾았다면?
if len(results[0].boxes) > 0:
    print("✅ YOLO: 번호판을 찾았습니다! 이미지를 자릅니다 ✂️")
    
    # 번호판의 [왼쪽 위, 오른쪽 아래] 좌표 가져오기
    box = results[0].boxes[0].xyxy[0].cpu().numpy()
    x1, y1, x2, y2 = map(int, box)
    
    # 💡 [핵심] OCR이 글자를 잘 읽도록 상하좌우에 여백(Padding) 15픽셀 주기!
    margin = 15
    # 사진 바깥으로 넘어가지 않도록 max, min으로 방어막을 쳐줍니다.
    x1 = max(0, x1 - margin)
    y1 = max(0, y1 - margin)
    x2 = min(img.shape[1], x2 + margin)
    y2 = min(img.shape[0], y2 + margin)
    
    # 여백을 포함해서 넉넉하게 자르기 (Crop)
    cropped_plate = img[y1:y2, x1:x2]
    
    # 2. 자른 이미지를 PaddleOCR에게 넘겨서 읽으라고 명령!
    print("🔎 PaddleOCR: 자른 번호판의 글자를 읽습니다...")
    ocr_result = ocr_model.ocr(cropped_plate, cls=True)
    
    predicted_text = ""
    if ocr_result and ocr_result[0]:
        # 자른 이미지는 평평하므로 단순히 왼쪽에서 오른쪽으로(X좌표) 정렬
        sorted_boxes = sorted(ocr_result[0], key=lambda x: x[0][0][0])
        for line in sorted_boxes:
            predicted_text += line[1][0]
            
        # 한글, 숫자만 남기기
        predicted_text = re.sub(r'[^가-힣0-9]', '', predicted_text)
        
    print(f"\n🎉 [최종 결과] AI가 인식한 글자: {predicted_text}")
    
    # 시각화 (결과를 눈으로 확인하는 창 띄우기)
    plt.imshow(cv2.cvtColor(cropped_plate, cv2.COLOR_BGR2RGB))
    plt.title(f"YOLO가 자른 이미지\n인식 결과: {predicted_text}")
    plt.axis('off')
    plt.show()

else:
    print("❌ 번호판을 찾지 못했습니다.")