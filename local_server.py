import cv2
import requests
from datetime import datetime
from ai_pipeline import RealTimePlateReader, LicensePlateEnsembler # 방금 만든 AI 불러오기

# 네이버 클라우드 중앙 서버 주소 (코드스페이스 포트포워딩 주소 또는 로컬호스트)
CENTRAL_SERVER_URL = "http://127.0.0.1:8000/api/entry"
PARKING_LOT_ID = "INHA_UNIV_01"

def run_local_camera():
    print("🎥 주차장 입구 카메라(AI 탑재)가 켜졌습니다...")
    
    # 1. 내가 만든 AI 번호판 인식기와 투표기(앙상블) 장착
    ai_reader = RealTimePlateReader('runs/detect/train3/weights/best.pt')
    ensembler = LicensePlateEnsembler(confidence_threshold=0.3)
    
    # 2. 테스트용 자동차 동영상 불러오기 (동영상 파일이 없다면 '0'을 넣어 웹캠을 켜도 됩니다)
# 2. 테스트용 자동차 동영상 불러오기 
    video_path = "images_car1.jpg"
    cap = cv2.VideoCapture(video_path) 
    
    frame_count = 0
    print("🚗 차량 진입 감지! AI 분석을 시작합니다...")

    # 30프레임(약 1초) 동안만 빠르게 번호판을 스캔합니다.
    while cap.isOpened() and frame_count < 150:
        ret, frame = cap.read()
        if not ret: break
            
        # AI가 사진을 보고 번호판을 읽습니다.
        plate_text, confidence = ai_reader.process_frame(frame)
        
        if plate_text:
            ensembler.add_frame_result(plate_text, confidence)
            print(f"[{frame_count}/30] AI 인식 중... : {plate_text} (확신도: {confidence:.2f})")
            
        frame_count += 1

    cap.release()
    
    # 3. 분석 결과를 종합하여 최종 번호판 도출
    final_plate, msg = ensembler.get_final_result()
    
    if final_plate:
        print(f"\n🎯 [최종 판독 완료] 차량 번호: {final_plate}")
        print("🌐 네이버 클라우드 중앙 서버로 데이터를 전송합니다...")
        
        # 4. 중앙 서버로 데이터 쏘기!
        payload = {
            "plate_number": final_plate,
            "parking_lot_id": PARKING_LOT_ID,
            "entry_time": datetime.now().isoformat()
        }
        
        try:
            response = requests.post(CENTRAL_SERVER_URL, json=payload)
            print("📬 중앙 서버 응답:", response.json())
        except Exception as e:
            print("❌ 서버 전송 실패:", e)
    else:
        print("\n❌ 번호판을 명확히 인식하지 못했습니다. 차단기를 열지 않습니다.")

if __name__ == "__main__":
    run_local_camera()