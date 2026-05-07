import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import hashlib
import requests

app = FastAPI(title="주차장 중앙 메인 서버")

SALT = "NAVER_AUTOPAY_SECRET_2026"
NAVER_PAY_URL = "http://127.0.0.1:9000/api/pay"
MY_WEBHOOK_URL = "http://127.0.0.1:8000/api/webhook/payment-result"

def encrypt_plate(plate_number: str) -> str:
    salted = plate_number + SALT
    return hashlib.sha256(salted.encode()).hexdigest()

REGISTERED_HASHES = [
    encrypt_plate("38거8243"), 
    encrypt_plate("52호5217"), 
    encrypt_plate("12가3456")
]

class EntryRequest(BaseModel):
    plate_number: str # 로컬 서버에서는 원본 번호를 받음
    parking_lot_id: str
    entry_time: str

class ExitRequest(BaseModel):
    car_id: str # 로컬 서버에서는 원본 번호를 받음
    fee: int

@app.post("/api/entry")
async def handle_vehicle_entry(request: EntryRequest):
    print(f"\n🏢 [중앙 서버] [{request.parking_lot_id}] 차량 입차 데이터 수신 완료!")
    
    # 💡 [핵심 보안] 중앙 서버가 자체적으로 해시 암호화하여 DB와 대조!
    hashed_plate = encrypt_plate(request.plate_number)
    is_naver_user = hashed_plate in REGISTERED_HASHES
    
    if is_naver_user:
        print(f"✅ 네이버 DB 해시 매칭 성공! (익명 토큰: {hashed_plate[:8]}...)")
        return {"open_gate": True, "message": "네이버 오토페이 유저 확인 완료"}
    else:
        print("❌ 등록되지 않은 데이터입니다.")
        return {"open_gate": False, "message": "미등록 유저 - 일반 발권 진행"}

@app.post("/api/request-exit")
async def handle_exit_request(request: ExitRequest):
    print(f"\n🏢 [중앙 서버] '{request.car_id}' 출차 요청 수신. 정산 요금: {request.fee}원")
    
    # 💡 [보안 패치] 차량 번호를 네이버페이로 넘기기 전에 '단방향 해시 암호'로 변환합니다!
    payment_token = encrypt_plate(request.car_id)
    print(f"🔒 [보안] 차량 번호를 결제용 익명 토큰으로 변환 완료: {payment_token[:15]}...")
    
    # 원본 car_id 대신 payment_token을 보냅니다.
    payload = {
        "payment_token": payment_token, 
        "fee": request.fee,
        "webhook_url": MY_WEBHOOK_URL
    }
    
    try:
        requests.post(NAVER_PAY_URL, json=payload)
    except Exception as e:
        return {"status": "ERROR", "message": "결제 서버 연결 실패"}
        
    return {"status": "PENDING", "message": "결제 진행 중. 차단기 대기."}

@app.post("/api/webhook/payment-result")
async def receive_payment_receipt(data: dict):
    payment_token = data.get("payment_token")
    status = data.get("status")
    
    print(f"\n🔔 [중앙 서버 웹훅 수신] 결제 토큰 '{payment_token[:8]}...' 상태: {status}")
    if status == "SUCCESS":
        print("🔓 [중앙 서버 -> 로컬 서버] 결제 완벽 확인! 차단기 개방 신호 전송!")
    return {"message": "영수증 수신 완료"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)