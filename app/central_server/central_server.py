import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import hashlib
import requests
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="주차장 중앙 메인 서버")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class AppUserRequest(BaseModel):
    user_id: str
    password: str = None

class AppUserIdRequest(BaseModel):
    user_id: str

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


# ==========================================
# 📱 [안드로이드 앱 연동 전용 API]
# ==========================================

@app.post("/signup")
async def app_signup(request: AppUserRequest):
    print(f"📱 [앱 연동] '{request.user_id}' 계정 회원가입 요청 수신")
    return {"status": "SUCCESS", "message": "회원가입이 완료되었습니다."}

@app.post("/login")
async def app_login(request: AppUserRequest):
    print(f"📱 [앱 연동] '{request.user_id}' 계정 로그인 요청 수신")
    return {"status": "SUCCESS", "message": "로그인 성공"}

@app.get("/parking/status")
async def app_get_parking_status(user_id: str):
    print(f"📱 [앱 연동] '{user_id}'님의 주차 상태 조회 요청")
    # TODO: 나중에 실제 CSV 데이터베이스를 읽어서 반환하도록 수정!
    # 일단은 앱 화면에 데이터가 잘 뜨는지 테스트하기 위한 더미(가짜) 데이터 전송
    return {
        "status": "PARKED",
        "plate_number": "38거8243",
        "entry_time": "2026-05-07 10:10:00",
        "current_fee": 2000
    }

@app.post("/parking/exit")
async def app_request_exit(request: AppUserIdRequest):
    print(f"📱 [앱 연동] '{request.user_id}'님이 앱에서 원격 출차/결제를 요청했습니다!")
    # TODO: 중앙 서버의 결제 모듈(네이버페이)과 연결하는 로직 추가 필요
    return {"status": "SUCCESS", "message": "출차 및 결제 요청이 접수되었습니다."}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)