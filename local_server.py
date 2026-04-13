import requests
import hashlib
import time
import random
from datetime import datetime

# 우리가 만든 AI 앙상블 클래스를 불러옵니다!
from ai_pipeline import LicensePlateEnsembler 

CENTRAL_SERVER_URL = "http://127.0.0.1:8000/api/entry"
SALT = "NAVER_AUTOPAY_SECRET_2026"

def encrypt_plate(plate_number):
    """차량 번호를 해시로 암호화"""
    salted_plate = plate_number + SALT
    return hashlib.sha256(salted_plate.encode()).hexdigest()

def send_entry_data(plate_number, parking_lot_id):
    """중앙 서버로 결제 승인 요청 전송"""
    encrypted_plate = encrypt_plate(plate_number)
    payload = {
        "plate_number": encrypted_plate,
        "parking_lot_id": parking_lot_id,
        "entry_time": datetime.now().isoformat()
    }
    
    print(f"🔒 [보안 통신] 네이버 클라우드로 해시 데이터 전송 중: {encrypted_plate[:15]}...")
    
    try:
        response = requests.post(CENTRAL_SERVER_URL, json=payload)
        result = response.json()
        
        if result["open_gate"]:
            print("🟢 [응답] 네이버페이 확인 완료! 차단기를 개방합니다!\n")
        else:
            print("🔴 [응답] 미등록 유저입니다. 일반 발권기로 안내합니다.\n")
            
    except requests.exceptions.ConnectionError:
        print("⚠️ [장애] 중앙 서버 통신 불가. 엣지 컴퓨팅(오프라인) 모드로 전환합니다.\n")

def run_automated_gate_system():
    """카메라 AI 분석부터 서버 전송까지의 전체 자동화 프로세스"""
    print("\n" + "="*50)
    print("🚗 [CCTV 가동] 차량 진입 감지! AI 분석을 시작합니다...")
    print("="*50)
    
    ensembler = LicensePlateEnsembler()
    
    # 카메라가 3초간 90프레임을 찍는 과정을 시뮬레이션
    for i in range(1, 91):
        if random.random() < 0.7:
            text, conf = "12가3456", round(random.uniform(0.7, 0.99), 2)
        else:
            text, conf = random.choice(["12가3458", "12다3456"]), round(random.uniform(0.4, 0.7), 2)
        ensembler.add_frame_result(text, conf)
        time.sleep(0.01) # 빠른 시연을 위해 대기 시간 단축

    # AI의 최종 결단
    final_plate, status_msg = ensembler.get_final_result()
    print(f"🧠 [AI 최종 판단] 번호: {final_plate} | 상태: {status_msg}")

    # 킬러 로직: AI가 '최종 승인'을 내렸을 때만 서버로 결제 요청을 보냄
    if "최종 승인 완료" in status_msg:
        print("🚀 [승인] 오인식 위험 없음. 네이버 클라우드로 결제를 요청합니다!")
        send_entry_data(final_plate, "A101")
    else:
        print("🛑 [차단] 인식률 저하(오결제 위험). 서버로 데이터를 보내지 않고 수동 결제로 우회합니다.")

if __name__ == "__main__":
    # 시스템 무한 가동 (실제 환경처럼 계속 차량을 기다림)
    while True:
        run_automated_gate_system()
        time.sleep(5) # 다음 차량이 들어올 때까지 5초 대기