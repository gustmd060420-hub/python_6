import os
import cv2
import numpy as np
from ultralytics import YOLO
import collections

# 에러 방지 설정
os.environ['FLAGS_enable_mkldnn'] = '0'

class RealTimePlateReader:
    def __init__(self, yolo_model_path='runs/detect/train3/weights/best.pt'):
        print("🧠 찐 AI 엔진(Paddle 2.6.2) 가동 준비 중...")
        self.yolo = YOLO(yolo_model_path)
        
        from paddleocr import PaddleOCR
        # 에러를 유발했던 show_log 등을 완벽히 제거한 순정 모드
        self.ocr_reader = PaddleOCR(lang='korean', use_angle_cls=False)
        print("✅ 진짜 AI 뇌(PaddleOCR) 탑재 완료!")

    def process_frame(self, frame_image):
        results = self.yolo(frame_image, verbose=False)
        
        for result in results:
            for box in result.boxes:
                # 1. YOLO가 번호판 네모 박스를 찾음!
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                pad = 10
                y1_p, y2_p = max(0, y1-pad), min(frame_image.shape[0], y2+pad)
                x1_p, x2_p = max(0, x1-pad), min(frame_image.shape[1], x2+pad)
                cropped = frame_image[y1_p:y2_p, x1_p:x2_p]
                
                # 2. OCR이 글자를 또렷하게 읽도록 명암 전처리 및 뻥튀기
                gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                enhanced = clahe.apply(gray)
                bigger = cv2.resize(enhanced, None, fx=2, fy=2)
                color_ready = cv2.cvtColor(bigger, cv2.COLOR_GRAY2BGR)
                
                # 3. 진짜 PaddleOCR 가동
                ocr_res = self.ocr_reader.ocr(color_ready)
                if ocr_res and ocr_res[0]:
                    for line in ocr_res[0]:
                        text, prob = line[1][0], line[1][1]
                        clean_text = "".join(filter(str.isalnum, text))
                        
                        # 한국 번호판 길이(최소 4글자 이상)일 때만 정답으로 인정
                        if len(clean_text) >= 4:
                            return clean_text, prob

        return None, 0.0

class LicensePlateEnsembler:
    def __init__(self, confidence_threshold=0.3): # 확신도 30% 이상만 취급
        self.confidence_threshold = confidence_threshold
        self.results = collections.defaultdict(float)
        
    def add_frame_result(self, text, conf):
        if conf >= self.confidence_threshold:
            self.results[text] += conf
            
    def get_final_result(self):
        if not self.results: return None, "인식 실패"
        return max(self.results, key=self.results.get), "최종 확정"