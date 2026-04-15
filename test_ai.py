from ultralytics import YOLO

# 내 AI 뇌 불러오기
model = YOLO('runs/detect/train3/weights/best.pt')

# 사진을 분석하고, 결과 화면에 띄워주기
results = model('images_car1.jpg', show=True)

# 아무 키나 누를 때까지 화면 유지
import cv2
cv2.waitKey(0)