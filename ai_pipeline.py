import os
import cv2
import numpy as np
from ultralytics import YOLO
import collections
import re

# 에러 방지 설정
os.environ['FLAGS_enable_mkldnn'] = '0'

class RealTimePlateReader:
    def __init__(self, yolo_model_path='runs/detect/train3/weights/best.pt'):
        print("🧠 찐 AI 엔진(Paddle 2.6.2) 가동 준비 중...")
        self.yolo = YOLO(yolo_model_path)
        
        from paddleocr import PaddleOCR
        self.ocr_reader = PaddleOCR(lang='korean', use_angle_cls=False)
        print("✅ 진짜 AI 뇌(PaddleOCR) 탑재 완료!")

    def process_frame(self, frame_image):
        results = self.yolo(frame_image, verbose=False)
        
        for result in results:
            for box in result.boxes:
                # 1. YOLO 번호판 추출
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                pad = 10
                y1_p, y2_p = max(0, y1-pad), min(frame_image.shape[0], y2+pad)
                x1_p, x2_p = max(0, x1-pad), min(frame_image.shape[1], x2+pad)
                cropped = frame_image[y1_p:y2_p, x1_p:x2_p]
                
                # 2. 전처리 (가장 잘 되었던 기본 모드)
                gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                enhanced = clahe.apply(gray)
                bigger = cv2.resize(enhanced, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                color_ready = cv2.cvtColor(bigger, cv2.COLOR_GRAY2BGR)
                
                # 3. OCR 실행
                ocr_res = self.ocr_reader.ocr(color_ready)
                
                if ocr_res and ocr_res[0]:
                    # ⭐ 핵심: 발견된 글자 뭉치들을 '왼쪽(x좌표)' 기준으로 정렬합니다.
                    # 이렇게 해야 '3725786조'가 아니라 '786조3725'로 합쳐집니다.
                    sorted_res = sorted(ocr_res[0], key=lambda x: x[0][0][0])
                    
                    raw_text = ""
                    max_prob = 0.0
                    for line in sorted_res:
                        raw_text += line[1][0]
                        max_prob = max(max_prob, line[1][1])

                    # 특수문자 제거
                    clean_text = "".join(re.findall(r'[0-9가-힣]', raw_text))
                    
                    # 4. 정규표현식으로 최종 번호 추출
                    match = re.search(r'(\d{2,3}[가-힣]\d{4})', clean_text)
                    if match:
                        return match.group(1), max_prob
                    elif len(clean_text) >= 4:
                        return clean_text, max_prob

        return None, 0.0

class LicensePlateEnsembler:
    def __init__(self, confidence_threshold=0.3):
        self.confidence_threshold = confidence_threshold
        self.results = collections.defaultdict(float)
        
    def add_frame_result(self, text, conf):
        if conf >= self.confidence_threshold:
            self.results[text] += conf
            
    def get_final_result(self):
        if not self.results: return None, "인식 실패"
        return max(self.results, key=self.results.get), "최종 확정"