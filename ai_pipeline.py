import os
import cv2
import numpy as np
from ultralytics import YOLO
import collections
import re

# 에러 방지 설정
os.environ['FLAGS_enable_mkldnn'] = '0'

class RealTimePlateReader:
    # 💡 YOLO 모델 경로를 아까 옮겨둔 'best.pt'로 수정했습니다.
    def __init__(self, yolo_model_path='best.pt'):
        print("🧠 찐 AI 엔진 가동 준비 중...")
        self.yolo = YOLO(yolo_model_path)
        
        from paddleocr import PaddleOCR
        # show_log=False를 추가해서 터미널이 지저분해지는 것을 막습니다.
        self.ocr_reader = PaddleOCR(lang='korean', use_angle_cls=True, show_log=False)
        print("✅ 진짜 AI 뇌(YOLO + PaddleOCR 콤보) 탑재 완료!")

    def process_frame(self, frame_image):
        results = self.yolo(frame_image, verbose=False)
        
        for result in results:
            # YOLO가 번호판을 찾았을 때만 실행
            if len(result.boxes) > 0:
                for box in result.boxes:
                    # 1. YOLO 번호판 추출
                    # 좌표를 추출할 때 .cpu().numpy()를 붙여 안전하게 가져옵니다.
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                    
                    # ⭐ 핵심: 마법의 15픽셀 여백 주기!
                    pad = 15
                    y1_p, y2_p = max(0, y1-pad), min(frame_image.shape[0], y2+pad)
                    x1_p, x2_p = max(0, x1-pad), min(frame_image.shape[1], x2+pad)
                    
                    # 여백을 포함해서 자르기 (전처리 없이 원본 컬러 유지!)
                    cropped = frame_image[y1_p:y2_p, x1_p:x2_p]
                    
                    # 2. OCR 실행 (자른 이미지를 그대로 투입)
                    ocr_res = self.ocr_reader.ocr(cropped, cls=True)
                    
                    if ocr_res and ocr_res[0]:
                        # 3. 텍스트 후처리: 발견된 글자들을 X좌표(왼쪽에서 오른쪽) 기준으로 정렬
                        sorted_res = sorted(ocr_res[0], key=lambda x: x[0][0][0])
                        
                        raw_text = ""
                        max_prob = 0.0
                        for line in sorted_res:
                            raw_text += line[1][0]
                            max_prob = max(max_prob, line[1][1])

                        # 특수문자 제거 (한글과 숫자만 남김)
                        clean_text = "".join(re.findall(r'[0-9가-힣]', raw_text))
                        
                        # 4. 정규표현식으로 최종 번호 추출 (예: 12가3456)
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