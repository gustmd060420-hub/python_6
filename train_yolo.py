from ultralytics import YOLO

# 1. 사전 학습된 가장 가벼운 YOLOv8 나노 모델을 불러옵니다.
model = YOLO('yolov8n.pt') 

print("🚀 번호판 탐지 모델 학습을 시작합니다... (저사양 최적화 모드)")

# 2. 메모리 부족(Terminated)을 막기 위해 옵션을 대폭 낮춥니다.
results = model.train(
    data='korea-car-plat-1/data.yaml', 
    epochs=50, 
    imgsz=320,       # 이미지 크기를 640에서 320으로 반토막 냅니다.
    batch=4,         # 한 번에 16장이 아닌 4장씩만 조심조심 넘깁니다.
    workers=0        # 백그라운드 작업을 꺼서 메모리를 아낍니다.
)

print("✅ 학습 완료! 최고 성능의 모델이 'runs/detect/train/weights/best.pt'에 저장되었습니다.")