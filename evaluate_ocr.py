import os
import difflib
import matplotlib.pyplot as plt
from paddleocr import PaddleOCR
import re
import cv2         # <-- 추가 (OpenCV)
import numpy as np # <-- 추가 (수학 연산)

# 윈도우 터미널 및 그래프 한글 깨짐 방지 폰트 설정
plt.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False

# OCR 엔진 초기화 (최초 실행 시 모델 다운로드 될 수 있음)
print("OCR 엔진을 불러오는 중입니다...")
ocr = PaddleOCR(use_angle_cls=True, lang='korean', show_log=False)

# 테스트 데이터 폴더 경로
data_dir = 'ocr_test_data'
results = []

total_images = 0
exact_matches = 0

print("\n=== [채점 시작] ===")

# 폴더 내의 모든 이미지 파일 순회
for filename in os.listdir(data_dir):
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        continue

    total_images += 1
    
    # 1. 정답 추출: 파일 이름에서 확장자(.jpg) 떼고 모든 띄어쓰기 제거
    ground_truth = os.path.splitext(filename)[0].replace(" ", "")

    # 2. 이미지 전처리 및 OCR 인식
    img_path = os.path.join(data_dir, filename)
    
    # 전처리 없이 원본 이미지 경로를 그대로 AI에게 넘김 (32% 달성 버전)
    result = ocr.ocr(img_path, cls=True)

    # 3. AI가 인식한 텍스트 합치기 및 후처리 (해상도 자동 맞춤 정렬!)
    predicted_text = ""
    if result and result[0]:
        boxes = result[0]
        # 꿀팁: AI가 찾은 글자 박스들의 '평균 높이'를 계산합니다.
        avg_height = sum([box[0][2][1] - box[0][0][1] for box in boxes]) / len(boxes)
        
        # 고정된 30픽셀이 아니라, 각 사진의 '평균 글자 높이의 절반'을 기준으로 줄(Line)을 나눕니다.
        sorted_result = sorted(boxes, key=lambda box: (box[0][0][1] // (avg_height * 0.5), box[0][0][0])) 
        
        for line in sorted_result:
            predicted_text += line[1][0]
            
    # 한글과 숫자만 남기고 모든 특수기호(-, ., 공백 등) 강제 삭제
    predicted_text = re.sub(r'[^가-힣0-9]', '', predicted_text)

    # 4. 시스템 인식 성공률 채점 (100% 똑같은가?)
    is_exact_match = (predicted_text == ground_truth)
    if is_exact_match:
        exact_matches += 1

    # 5. 글자 단위 인식률 채점 (몇 글자나 맞췄는가?)
    # SequenceMatcher를 써서 문자열 간의 유사도를 %로 계산합니다.
    matcher = difflib.SequenceMatcher(None, ground_truth, predicted_text)
    char_acc = matcher.ratio() * 100

    # 결과 기록
    results.append({'char_acc': char_acc})
    
    # 채점 결과 화면에 출력 (O / X 표시)
    mark = "✅" if is_exact_match else "❌"
    print(f"[{total_images:02d}] 정답: {ground_truth:10} | AI 예측: {predicted_text:10} | 정확도: {char_acc:6.1f}% | {mark}")

# === 최종 통계 계산 ===
system_accuracy = (exact_matches / total_images) * 100 if total_images > 0 else 0
avg_char_accuracy = sum(r['char_acc'] for r in results) / total_images if total_images > 0 else 0

print("\n" + "="*45)
print(f"총 테스트 이미지: {total_images}장")
print(f"🎯 최종 시스템 인식 성공률: {system_accuracy:.1f}% ({exact_matches}/{total_images})")
print(f"🔤 평균 글자 단위 인식률: {avg_char_accuracy:.1f}%")
print("="*45 + "\n")

# === 평가 결과 그래프 그리기 (시각화) ===
print("결과 그래프를 생성하고 있습니다...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# 왼쪽 그래프: 최종 시스템 성공률 (파이 차트)
labels = ['성공 (100% 일치)', '실패 (오타 존재)']
sizes = [exact_matches, total_images - exact_matches]
colors = ['#4CAF50', '#F44336'] # 초록, 빨강
explode = (0.1, 0) # 성공 부분만 살짝 떼어내서 강조

ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=90, textprops={'fontsize': 12})
ax1.set_title('최종 시스템 인식 성공률 (Exact Match)', fontsize=14, fontweight='bold')

# 오른쪽 그래프: 글자 단위 인식률 분포 (히스토그램)
char_accs = [r['char_acc'] for r in results]
ax2.hist(char_accs, bins=10, range=(0, 100), color='#2196F3', edgecolor='black', alpha=0.7)
ax2.set_title('글자 단위 인식률 분포도', fontsize=14, fontweight='bold')
ax2.set_xlabel('글자 단위 정확도 (%)', fontsize=12)
ax2.set_ylabel('이미지 개수 (장)', fontsize=12)
ax2.grid(axis='y', linestyle='--', alpha=0.7)

# 파일로 저장 후 화면에 띄우기
plt.tight_layout()
plt.savefig('evaluation_results.png', dpi=300)
print("📊 'evaluation_results.png' 파일이 저장되었습니다. 창을 닫으면 프로그램이 종료됩니다.")
plt.show()