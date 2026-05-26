import os
import cv2
import time
import serial
import requests
from datetime import datetime
from ai_pipeline import RealTimePlateReader, LicensePlateEnsembler
import hashlib

# ─── ⚙️ 통합 환경 설정 ────────────────────────────────────────────────────────
CENTRAL_SERVER = "http://127.0.0.1:8000"
PARKING_LOT_ID = "INHA_UNIV_01"
SALT = "NAVER_AUTOPAY_SECRET_2026"

# 하드웨어 통신 설정
ARDUINO_PORT = 'COM3'  # 본인 포트에 맞게 수정
BAUD_RATE = 9600

# 현재 단말기 모드 설정 (입차 테스트 시 "ENTRY", 출차 테스트 시 "EXIT")
CURRENT_MODE = "ENTRY"  

MAX_RETRIES = 2          
GATE_POLL_INTERVAL = 1   
GATE_POLL_MAX = 15       

# ─── 헬퍼 함수 ──────────────────────────────────────────────────────────────
def encrypt_plate(plate: str) -> str:
    return hashlib.sha256((plate + SALT).encode()).hexdigest()

def _poll_gate(payment_token: str) -> bool:
    print("💳 결제 완료 대기 중...", end="", flush=True)
    for _ in range(GATE_POLL_MAX):
        time.sleep(GATE_POLL_INTERVAL)
        try:
            resp = requests.get(f"{CENTRAL_SERVER}/api/gate-status",
                                params={"payment_token": payment_token}, timeout=3)
            if resp.json().get("open_gate"):
                print(" ✅ 차단기 개방 승인!")
                return True
        except Exception:
            pass
        print(".", end="", flush=True)
    print(" ❌ 타임아웃")
    return False

def _recognize_plate_from_webcam(ai_reader):
    """아두이노 신호가 오면 즉시 웹캠을 켜서 번호판을 인식합니다."""
    print("📷 웹캠 가동 중...")
    ensembler = LicensePlateEnsembler(confidence_threshold=0.3)
    
    # 0번은 기본 웹캠 (노트북 내장 카메라 또는 USB 캠)
    # 만약 웹캠이 없고 테스트 영상으로 대체하려면 0 대신 "../../data/media/test_video1.mp4" 입력
    cap = cv2.VideoCapture(0) 
    
    valid_frames = 0
    start_time = time.time()

    # 최대 5초 동안만 카메라를 켜서 확인 (무한 대기 방지)
    while cap.isOpened() and (time.time() - start_time) < 5.0:
        ret, frame = cap.read()
        if not ret:
            break
            
        plate_text, confidence = ai_reader.process_frame(frame)
        if plate_text:
            ensembler.add_frame_result(plate_text, confidence)
            valid_frames += 1
            print(f"   -> [판독 중] {plate_text} (신뢰도: {confidence:.2f})")
            
        if valid_frames >= 15: # 15 프레임(약 0.5초)만 모이면 바로 확정 지어 속도 향상
            break

    cap.release()
    final_plate, _ = ensembler.get_final_result()
    if not final_plate:
        return None, None
    return final_plate, encrypt_plate(final_plate)


# ─── 🚀 메인 하드웨어 제어 루프 ─────────────────────────────────────────────
def run_integrated_terminal():
    print(f"==== PY-Pass {CURRENT_MODE} 통합 단말기 가동 ====")
    
    # 1. AI 엔진 초기화
    ai_reader = RealTimePlateReader('../../models/best.pt')
    
    # 2. 아두이노 시리얼 통신 연결
    try:
        py_serial = serial.Serial(port=ARDUINO_PORT, baudrate=BAUD_RATE, timeout=1)
        time.sleep(2)
        print(f"✅ 아두이노({ARDUINO_PORT}) 연동 완료. 초음파 감지 대기 중...")
    except Exception as e:
        print(f"❌ 아두이노 연결 실패: {e}")
        return

    while True:
        try:
            if py_serial.in_waiting > 0:
                line = py_serial.readline().decode('utf-8').strip()
                
                # 아두이노에서 초음파 감지 신호('CAR_IN')가 들어왔을 때
                if line == "CAR_IN":
                    print(f"\n🚨 [초음파 감지] 차량 접근! AI 번호판 인식 프로세스 기동!")
                    
                    final_plate = None
                    payment_token = None

                    # 재시도 루프
                    for attempt in range(1, MAX_RETRIES + 1):
                        final_plate, payment_token = _recognize_plate_from_webcam(ai_reader)
                        if final_plate:
                            break
                        print(f"⚠️ 인식 실패. 재시도 {attempt}/{MAX_RETRIES}...")

                    if not final_plate:
                        print("❌ 번호판 인식 최종 실패. 차단기 유지.")
                        continue # 처음(감지 대기)으로 돌아감

                    print(f"\n🚙 [AI 최종 판독] {final_plate}")
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # ────────────────────────────────────────────────────
                    # [입차 모드] 서버 통신 로직
                    # ────────────────────────────────────────────────────
                    if CURRENT_MODE == "ENTRY":
                        resp = requests.post(f"{CENTRAL_SERVER}/api/entry", json={
                            "plate_number": final_plate,
                            "parking_lot_id": PARKING_LOT_ID,
                            "entry_time": now_str
                        })
                        result = resp.json()
                        print("🌐 중앙 서버 응답:", result)
                        
                        if result.get("open_gate"):
                            print("🔓 입차 승인! 아두이노 차단기 개방 명령 전송 (O)")
                            py_serial.write(b'O')
                            time.sleep(3) # 3초간 차단기 열림 유지
                            py_serial.write(b'C')
                            print("🔒 차량 통과 완료. 차단기 폐쇄 (C)")
                        else:
                            print("❌ 미등록 차량. 차단기 유지.")

                    # ────────────────────────────────────────────────────
                    # [출차 모드] 서버 통신 및 결제 로직
                    # ────────────────────────────────────────────────────
                    elif CURRENT_MODE == "EXIT":
                        resp = requests.post(f"{CENTRAL_SERVER}/api/request-exit", json={
                            "car_id": final_plate,
                            "fee": 0 
                        })
                        result = resp.json()
                        print("🌐 중앙 서버 응답:", result)

                        if result.get("status") == "ERROR":
                            print("❌ 출차 불가:", result.get("message"))
                            continue

                        # 결제(웹훅) 완료 폴링 확인
                        gate_opened = _poll_gate(payment_token)
                        if gate_opened:
                            print("🔓 결제 완료! 아두이노 차단기 개방 명령 전송 (O)")
                            py_serial.write(b'O')
                            time.sleep(3) # 3초간 차단기 열림 유지
                            py_serial.write(b'C')
                            print("🔒 차량 통과 완료. 차단기 폐쇄 (C)")
                        else:
                            print("⚠️ 결제 지연. 차단기 유지.")
                            
                    print("\n🔄 다음 차량 초음파 감지 대기 중...")
                    
        except KeyboardInterrupt:
            print("\n통합 단말기를 종료합니다.")
            py_serial.close()
            break
        except Exception as e:
            pass # 기타 자잘한 통신 에러 무시하고 루프 유지

if __name__ == "__main__":
    run_integrated_terminal()