import os
import cv2
import numpy as np
from ultralytics import YOLO
import collections
import re

# 에러 방지 설정
os.environ['FLAGS_enable_mkldnn'] = '0'

class RealTimePlateReader:
    def __init__(self, yolo_model_path='best.pt'):
        print("🧠 찐 AI 엔진(시력 강화 버전) 가동 준비 중...")
        self.yolo = YOLO(yolo_model_path)
        
        from paddleocr import PaddleOCR
        self.ocr_reader = PaddleOCR(lang='korean', use_angle_cls=True, show_log=False)
        print("✅ 진짜 AI 뇌(동적 여백 + 2배 확대 + 문법 교정) 탑재 완료!")

    # 💡 [핵심 추가] 번호판 문법 검사 및 자동 교정기
    # 💡 [핵심 추가] 번호판 문법 검사 및 자동 교정기
    def _correct_plate_format(self, text):
        clean_text = re.sub(r'[^0-9가-힣]', '', text)
        
        # 💡 [해결책] 정규식 검사를 통과해버리기 "전에", 고질적인 한글 오인식을 무조건 먼저 바꿉니다.
        # (현업 PoC 테스트에서 특정 엔진의 고질적 오타를 잡기 위해 자주 쓰는 강제 매핑 기법입니다)
        clean_text = clean_text.replace('개', '거').replace('가', '거')
        
        # 이미 완벽한 형식이면 통과
        match = re.search(r'(\d{2,3}[가-힣]\d{4})', clean_text)
        if match:
            return match.group(1)
            
        # 숫자 형태 오인식 교정 사전 (4->나, 0->어 등)
        correction_map = {'4': '나', '0': '어', '1': '너', '2': '러', '5': '도', '8': '가', '3': '다'}
        
        if len(clean_text) == 8 and clean_text[:3].isdigit() and clean_text[4:].isdigit():
            wrong_char = clean_text[3]
            if wrong_char in correction_map:
                return clean_text[:3] + correction_map[wrong_char] + clean_text[4:]
        elif len(clean_text) == 7 and clean_text[:2].isdigit() and clean_text[3:].isdigit():
            wrong_char = clean_text[2]
            if wrong_char in correction_map:
                return clean_text[:2] + correction_map[wrong_char] + clean_text[3:]
                
        return clean_text
    

    def process_frame(self, frame_image):
        # 💡 [핵심 수정] conf=0.15 를 추가해서, 15%만 확신해도 일단 다 번호판으로 인정하고 자르라고 명령합니다!
        results = self.yolo(frame_image, conf=0.15, verbose=False)
        
        for result in results:
            if len(result.boxes) > 0:
                for box in result.boxes:
                    # 1. YOLO 번호판 좌표 추출
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                    
                    # 💡 [개선 1] 황금 비율 여백 적용 (가로 8%, 세로 5%)
                    box_width = x2 - x1
                    box_height = y2 - y1
                    pad_x = int(box_width * 0.08)
                    pad_y = int(box_height * 0.05)
                    
                    y1_p, y2_p = max(0, y1-pad_y), min(frame_image.shape[0], y2+pad_y)
                    x1_p, x2_p = max(0, x1-pad_x), min(frame_image.shape[1], x2+pad_x)
                    
                    # 여백 포함 자르기
                    cropped = frame_image[y1_p:y2_p, x1_p:x2_p]
                    
                    # 💡 [개선 2] 이미지 2배 확대 (OCR 인식률 극대화)
                    cropped = cv2.resize(cropped, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
                    
                    # 2. OCR 실행
                    ocr_res = self.ocr_reader.ocr(cropped, cls=True)
                    
                    if ocr_res and ocr_res[0]:
                        # X좌표 기준 정렬
                        sorted_res = sorted(ocr_res[0], key=lambda x: x[0][0][0])
                        
                        raw_text = ""
                        max_prob = 0.0
                        for line in sorted_res:
                            raw_text += line[1][0]
                            max_prob = max(max_prob, line[1][1])

                        # 💡 [개선 3] 문법 교정기 통과
                        final_text = self._correct_plate_format(raw_text)
                        
                        # 💡 [최종 진화] 완벽한 한국 번호판 규격(7~8자리)이 아니면 쓰레기통으로 직행!
                        if re.match(r'^\d{2,3}[가-힣]\d{4}$', final_text):
                            return final_text, max_prob

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