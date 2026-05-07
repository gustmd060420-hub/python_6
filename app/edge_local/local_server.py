import cv2
import requests
import hashlib
from datetime import datetime
from ai_pipeline import RealTimePlateReader, LicensePlateEnsembler

# 💡 1. 팀원이 만든 요금 정산 모듈 불러오기!
from fee_calculator import NaverAutoPass

# 💡 2. 팀원의 시스템(CSV DB) 장착
parking_system = NaverAutoPass('../../data/db/parking_logs_v3.csv')

def run_local_camera(video_path, camera_mode="ENTRY"):
    print(f"\n🎥 주차장 [{camera_mode}] 카메라(AI 탑재)가 켜졌습니다...")
    
    ai_reader = RealTimePlateReader('../../models/best.pt')
    ensembler = LicensePlateEnsembler(confidence_threshold=0.3)
    cap = cv2.VideoCapture(video_path) 
    
    valid_frames = 0 
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
            
        plate_text, confidence = ai_reader.process_frame(frame)
        if plate_text:
            ensembler.add_frame_result(plate_text, confidence)
            valid_frames += 1 
            print(f"[{valid_frames}/30] 스캔 중... : {plate_text} (확신도: {confidence:.2f})")
            
        if valid_frames >= 30:
            break
    cap.release()
    
    final_plate, msg = ensembler.get_final_result()
    
    if final_plate:
        print(f"\n🎯 [AI 최종 판독] 차량 번호: {final_plate}")
        
        # 💡 3. AI가 번호를 넘겨주면, 팀원의 요금 정산 시스템 실행!
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("-" * 50)
        
        if camera_mode == "ENTRY":
            success, message = parking_system.process_entry(final_plate, now_str)
            print(message)
            
            # 💡 암호화는 중앙 서버가 담당하므로 로컬은 원본 데이터를 그대로 쏩니다.
            try:
                print("🌐 중앙 서버로 입차 데이터를 전송합니다...")
                resp = requests.post("http://127.0.0.1:8000/api/entry", 
                                     json={"plate_number": final_plate, "parking_lot_id": "INHA_UNIV_01", "entry_time": now_str})
                print("📬 중앙 서버 응답:", resp.json())
            except Exception as e:
                print(f"⚠️ 중앙 서버 통신 실패: {e}")

        elif camera_mode == "EXIT":
            # 1. 로컬 요금 계산기 실행
            success, message, final_fee = parking_system.process_settlement(final_plate, now_str) 
            print(message)
            
            # 2. 요금이 발생했다면 중앙 서버로 결제(출차) 요청!
            # 2. 요금이 발생했다면 중앙 서버로 결제(출차) 요청!
            if success and final_fee > 0:
                try:
                    print("🌐 중앙 서버로 결제 요청을 쏘고 대기합니다...")
                    # 💡 핵심 수정: numpy int64를 순수 python int로 캐스팅!
                    resp = requests.post("http://127.0.0.1:8000/api/request-exit", 
                                         json={"car_id": final_plate, "fee": int(final_fee)})
                    print("📬 중앙 서버 응답:", resp.json())
                except Exception as e:
                    print(f"⚠️ 중앙 서버 통신 실패: {e}") # 에러의 진짜 이유를 보도록 수정
        
    else:
        print("\n❌ 번호판 인식 실패. 차단기 유지.")

if __name__ == "__main__":
    # 🚗 [테스트 A] 1번 비디오 차량 사이클
    #run_local_camera("../../data/media/test_video1.mp4", camera_mode="ENTRY")
    run_local_camera("../../data/media/test_video1.mp4", camera_mode="EXIT")
    
    # 🚙 [테스트 B] 2번 비디오 차량 사이클
    #run_local_camera("../../data/media/test_video2.mp4", camera_mode="ENTRY")
    run_local_camera("../../data/media/test_video2.mp4", camera_mode="EXIT")