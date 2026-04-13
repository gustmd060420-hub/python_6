from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import hashlib

app = FastAPI()
SALT = "NAVER_AUTOPAY_SECRET_2026"

class EntryRequest(BaseModel):
    plate_number: str # 이제 여기엔 원본 번호가 아닌 해시 암호가 들어옵니다.
    parking_lot_id: str
    entry_time: datetime

def encrypt_plate(plate_number: str) -> str:
    salted = plate_number + SALT
    return hashlib.sha256(salted.encode()).hexdigest()

# 가상의 네이버 DB: 이제 DB에도 원본이 아닌 '해시 암호'만 저장되어 있습니다.
REGISTERED_HASHES = [
    encrypt_plate("12가3456"), # 등록된 유저
    encrypt_plate("98하7654")  # 등록된 유저
]

@app.post("/api/entry")
async def handle_vehicle_entry(request: EntryRequest):
    print(f"[{request.parking_lot_id}] 암호화된 차량 데이터 수신 완료!")
    
    # 들어온 암호가 우리 DB의 암호와 일치하는지 비교만 합니다. (원본은 알 필요 없음)
    is_naver_user = request.plate_number in REGISTERED_HASHES
    
    if is_naver_user:
        print("✅ 네이버 DB 해시 매칭 성공!")
        return {"open_gate": True, "message": "네이버 오토페이 유저 확인 완료"}
    else:
        print("❌ 등록되지 않은 해시 데이터입니다.")
        return {"open_gate": False, "message": "미등록 유저 - 일반 발권 진행"}