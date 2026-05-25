import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../edge_local'))

import math
import hashlib
import requests
import pandas as pd
import uvicorn
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fee_calculator import NaverAutoPass

app = FastAPI(title="주차장 통합 서버")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── 설정 ──────────────────────────────────────────────────────────────────────
SALT = "NAVER_AUTOPAY_SECRET_2026"
MOCK_PG_URL = "http://127.0.0.1:9000/api/pay"
MY_WEBHOOK_URL = "http://127.0.0.1:8000/api/webhook/payment-result"
CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data/db/parking_logs_v3.csv')

DAILY_MAX_FEE = 30000
BASE_FEE_PER_10MIN = 1000

parking_system = NaverAutoPass(CSV_PATH)


def encrypt_plate(plate: str) -> str:
    return hashlib.sha256((plate + SALT).encode()).hexdigest()


# 등록 차량 해시 (차량 등록 시 동적으로 추가됨)
REGISTERED_HASHES: set = {
    encrypt_plate("38거8243"),
    encrypt_plate("52호5217"),
    encrypt_plate("12가3456"),
}

# ─── 인메모리 앱 데이터 ────────────────────────────────────────────────────────
user_db = {}
car_db = {}    # user_id -> [{"plate", "model", "color", "year", "is_default"}]
card_db = {}   # user_id -> [{"card_number", "bank", "color", "is_default"}]
coupon_db = {} # user_id -> [{"title", "description", "expires_at", "is_available"}]

# AI 카메라가 입차 신호 보낼 때 위치 기록 (plate -> {"location", "entry_time"})
plate_location_db = {}

# 결제 완료 후 차단기 개방 신호 (normalized_plate -> True)
gate_db = {}

coupon_code_db = {
    "PYPASS30":  {"title": "30분 무료 주차",  "description": "Py-Pass 전용 혜택", "expires_at": "2025-12-31"},
    "PYPASS1H":  {"title": "1시간 무료 주차", "description": "특별 할인 쿠폰",   "expires_at": "2025-12-31"},
    "WELCOME10": {"title": "10% 할인 쿠폰",   "description": "신규 가입 혜택",    "expires_at": "2025-12-31"},
}

# ─── 모델 ──────────────────────────────────────────────────────────────────────
class User(BaseModel):
    user_id: str
    password: str
    name: str = None

class UserIdRequest(BaseModel):
    user_id: str

class ParkRequest(BaseModel):
    user_id: str
    location: str

class CarRequest(BaseModel):
    user_id: str
    plate: str
    model: str
    color: str
    year: str

class PlateRequest(BaseModel):
    user_id: str
    plate: str

class CardRequest(BaseModel):
    user_id: str
    card_number: str
    bank: str
    color: str

class CardDeleteRequest(BaseModel):
    user_id: str
    card_number: str

class CouponRequest(BaseModel):
    user_id: str
    title: str
    description: str
    expires_at: str
    is_active: bool = True

class CouponRedeemRequest(BaseModel):
    user_id: str
    coupon_code: str

class UserUpdateNameRequest(BaseModel):
    user_id: str
    name: str

class SetDefaultCarRequest(BaseModel):
    user_id: str
    plate: str

# AI 카메라 전용
class EntryRequest(BaseModel):
    plate_number: str
    parking_lot_id: str
    entry_time: str

class ExitRequest(BaseModel):
    car_id: str
    fee: int

# ─── 헬퍼 ──────────────────────────────────────────────────────────────────────
def _calc_fee_str(entry_time_str: str) -> str:
    """입차 시간 기준 현재 요금 계산 (fee_calculator와 동일 공식)"""
    try:
        fmt = "%Y-%m-%d %H:%M:%S"
        entry_dt = datetime.strptime(entry_time_str, fmt)
        duration_min = (datetime.now() - entry_dt).total_seconds() / 60.0
        total = (int(duration_min // (24 * 60)) * DAILY_MAX_FEE) + \
                min(DAILY_MAX_FEE, math.ceil(max(1, duration_min) / 10) * BASE_FEE_PER_10MIN)
        return str(total) + "원"
    except Exception:
        return "계산 불가"


def _find_parked_plate(user_id: str):
    """
    user_id 소유 차량 중 CSV에 미출차 상태인 번호판 반환.
    반환: (plate, entry_time_str) 또는 (None, None)
    """
    parking_system.load_db()
    user_plates = {c["plate"].replace(" ", "") for c in car_db.get(user_id, [])}
    if not user_plates:
        return None, None

    for _, row in parking_system.db.iterrows():
        plate = str(row["차량 번호"]).replace(" ", "")
        if plate in user_plates and pd.isna(row["출차 일시"]):
            return str(row["차량 번호"]), str(row["입차 일시"])
    return None, None


# ─── 회원 API ──────────────────────────────────────────────────────────────────
@app.post("/signup")
def signup(user: User):
    if user.user_id in user_db:
        raise HTTPException(status_code=400, detail="이미 존재하는 아이디입니다.")
    user_db[user.user_id] = {"password": user.password, "name": user.name}
    car_db[user.user_id] = []
    card_db[user.user_id] = []
    coupon_db[user.user_id] = []
    print(f"📱 [앱] '{user.user_id}' 회원가입 완료")
    return {"message": "회원가입 완료"}


@app.post("/login")
def login(user: User):
    if user.user_id not in user_db or user_db[user.user_id]["password"] != user.password:
        raise HTTPException(status_code=401, detail="정보가 일치하지 않습니다.")
    car_db.setdefault(user.user_id, [])
    card_db.setdefault(user.user_id, [])
    coupon_db.setdefault(user.user_id, [])
    print(f"📱 [앱] '{user.user_id}' 로그인")
    return {"message": "로그인 성공", "name": user_db[user.user_id]["name"]}


@app.get("/user/info")
def get_user_info(user_id: str):
    if user_id not in user_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return {"user_id": user_id, "name": user_db[user_id]["name"]}


@app.post("/user/update-name")
def update_user_name(req: UserUpdateNameRequest):
    if req.user_id not in user_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    user_db[req.user_id]["name"] = req.name
    return {"message": "이름이 변경되었습니다."}


@app.post("/user/delete")
def delete_user(req: UserIdRequest):
    if req.user_id not in user_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    user_db.pop(req.user_id, None)
    car_db.pop(req.user_id, None)
    card_db.pop(req.user_id, None)
    coupon_db.pop(req.user_id, None)
    return {"message": "회원 탈퇴가 완료되었습니다."}


# ─── 주차 상태 API ─────────────────────────────────────────────────────────────
@app.get("/parking/status")
def get_parking_status(user_id: str):
    """
    CSV DB에서 사용자 차량의 현재 주차 상태 조회.
    주차 중이면 위치/입차시각/요금 반환.
    """
    plate, entry_time = _find_parked_plate(user_id)

    if plate:
        normalized = plate.replace(" ", "")
        location_info = plate_location_db.get(normalized, {})
        location = location_info.get("location", "주차장")
        fee_str = _calc_fee_str(entry_time)
        print(f"📱 [앱] '{user_id}' 주차 중 - {plate} / {location} / {fee_str}")
        return {
            "is_parked": True,
            "location": location,
            "parked_time": entry_time,
            "fee": fee_str
        }

    print(f"📱 [앱] '{user_id}' 주차 없음")
    return {"is_parked": False}


@app.get("/parking/history")
def get_parking_history(user_id: str):
    """CSV에서 해당 유저 차량의 완료된 주차 이력 반환"""
    if user_id not in user_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    parking_system.load_db()
    user_plates = {c["plate"].replace(" ", "") for c in car_db.get(user_id, [])}
    history = []
    for _, row in parking_system.db.iterrows():
        plate = str(row["차량 번호"]).replace(" ", "")
        if plate in user_plates and not pd.isna(row.get("출차 일시", float("nan"))):
            fee_val = row.get("정산 금액", "")
            history.append({
                "location": str(row.get("주차장", "주차장")),
                "entry_time": str(row["입차 일시"]),
                "exit_time": str(row["출차 일시"]),
                "fee": str(int(fee_val)) + "원" if fee_val != "" and not pd.isna(fee_val) else "0원"
            })
    history.reverse()  # 최신 순
    return {"history": history}


@app.post("/parking/exit")
def exit_parking(req: UserIdRequest, background_tasks: BackgroundTasks):
    """
    앱에서 출차/결제 요청.
    CSV에서 해당 유저 차량을 정산하고 Mock PG로 결제 요청.
    """
    plate, _ = _find_parked_plate(req.user_id)
    if not plate:
        raise HTTPException(status_code=400, detail="주차된 차량 정보가 없습니다.")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    success, message, final_fee = parking_system.process_settlement(plate, now_str)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    # plate_location_db 정리
    plate_location_db.pop(plate.replace(" ", ""), None)

    print(f"📱 [앱] '{req.user_id}' 출차 정산 완료: {message}")

    # Mock PG 결제 비동기 호출 (요금이 있을 때만)
    if final_fee > 0:
        payment_token = encrypt_plate(plate)
        payload = {
            "payment_token": payment_token,
            "fee": int(final_fee),
            "webhook_url": MY_WEBHOOK_URL
        }
        background_tasks.add_task(_request_payment, payload)

    return {"status": "PENDING", "message": message}


def _request_payment(payload: dict):
    try:
        requests.post(MOCK_PG_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"⚠️ Mock PG 연결 실패: {e}")


# ─── 차량 API ──────────────────────────────────────────────────────────────────
@app.get("/cars")
def get_cars(user_id: str):
    if user_id not in user_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return {"cars": car_db.get(user_id, [])}


@app.post("/cars/add")
def add_car(req: CarRequest):
    if req.user_id not in user_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    cars = car_db.setdefault(req.user_id, [])
    if any(c["plate"] == req.plate for c in cars):
        raise HTTPException(status_code=400, detail="이미 등록된 번호판입니다.")
    cars.append({
        "plate": req.plate,
        "model": req.model,
        "color": req.color,
        "year": req.year,
        "is_default": len(cars) == 0
    })
    # AI 카메라 자동 인식을 위해 해시 등록
    REGISTERED_HASHES.add(encrypt_plate(req.plate))
    REGISTERED_HASHES.add(encrypt_plate(req.plate.replace(" ", "")))
    print(f"🚗 [차량 등록] {req.plate} → REGISTERED_HASHES 추가 완료")
    return {"message": "차량이 등록되었습니다."}


@app.post("/cars/set-default")
def set_default_car(req: SetDefaultCarRequest):
    if req.user_id not in user_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    cars = car_db.get(req.user_id, [])
    found = any(c["plate"] == req.plate for c in cars)
    if not found:
        raise HTTPException(status_code=404, detail="해당 차량을 찾을 수 없습니다.")
    for c in cars:
        c["is_default"] = (c["plate"] == req.plate)
    return {"message": "기본 차량이 설정되었습니다."}


@app.post("/cars/delete")
def delete_car(req: PlateRequest):
    if req.user_id not in user_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    cars = car_db.get(req.user_id, [])
    new_cars = [c for c in cars if c["plate"] != req.plate]
    if len(new_cars) == len(cars):
        raise HTTPException(status_code=404, detail="해당 차량을 찾을 수 없습니다.")
    car_db[req.user_id] = new_cars
    return {"message": "차량이 삭제되었습니다."}


# ─── 카드 API ──────────────────────────────────────────────────────────────────
@app.get("/cards")
def get_cards(user_id: str):
    if user_id not in user_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return {"cards": card_db.get(user_id, [])}


@app.post("/cards/add")
def add_card(req: CardRequest):
    if req.user_id not in user_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    cards = card_db.setdefault(req.user_id, [])
    if any(c["card_number"] == req.card_number for c in cards):
        raise HTTPException(status_code=400, detail="이미 등록된 카드입니다.")
    cards.append({
        "card_number": req.card_number,
        "bank": req.bank,
        "color": req.color,
        "is_default": len(cards) == 0
    })
    return {"message": "카드가 등록되었습니다."}


@app.post("/cards/delete")
def delete_card(req: CardDeleteRequest):
    if req.user_id not in user_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    cards = card_db.get(req.user_id, [])
    new_cards = [c for c in cards if c["card_number"] != req.card_number]
    if len(new_cards) == len(cards):
        raise HTTPException(status_code=404, detail="해당 카드를 찾을 수 없습니다.")
    card_db[req.user_id] = new_cards
    return {"message": "카드가 삭제되었습니다."}


# ─── 쿠폰 API ──────────────────────────────────────────────────────────────────
@app.get("/coupons")
def get_coupons(user_id: str):
    if user_id not in user_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return {"coupons": coupon_db.get(user_id, [])}


@app.post("/coupons/add")
def add_coupon(req: CouponRequest):
    if req.user_id not in user_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    coupons = coupon_db.setdefault(req.user_id, [])
    coupons.append({
        "title": req.title,
        "description": req.description,
        "expires_at": req.expires_at,
        "is_available": req.is_active
    })
    return {"message": "쿠폰이 등록되었습니다."}


@app.post("/coupons/redeem")
def redeem_coupon(req: CouponRedeemRequest):
    if req.user_id not in user_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    code = req.coupon_code.upper().strip()
    if code not in coupon_code_db:
        raise HTTPException(status_code=400, detail="유효하지 않은 쿠폰 코드입니다.")
    coupon_info = coupon_code_db[code]
    coupons = coupon_db.setdefault(req.user_id, [])
    coupons.append({
        "title": coupon_info["title"],
        "description": coupon_info["description"],
        "expires_at": coupon_info["expires_at"],
        "is_available": True
    })
    return {"message": coupon_info["title"] + " 쿠폰이 등록되었습니다."}


# ─── AI 카메라 연동 API ────────────────────────────────────────────────────────
@app.post("/api/entry")
async def handle_vehicle_entry(request: EntryRequest):
    """AI 카메라(local_server.py)에서 번호판 인식 후 호출"""
    print(f"\n🏢 [{request.parking_lot_id}] 입차 데이터 수신: {request.plate_number}")

    hashed = encrypt_plate(request.plate_number)
    is_registered = hashed in REGISTERED_HASHES

    # CSV에 입차 기록
    success, msg = parking_system.process_entry(request.plate_number, request.entry_time)
    print(msg)

    # 위치 정보 저장 (앱 상태 표시용)
    normalized = request.plate_number.replace(" ", "")
    plate_location_db[normalized] = {
        "location": request.parking_lot_id,
        "entry_time": request.entry_time
    }

    if is_registered:
        print(f"✅ 등록 차량 확인 (토큰: {hashed[:8]}...)")
        return {"open_gate": True, "message": "등록 차량 입차 완료"}
    else:
        print("❌ 미등록 차량")
        return {"open_gate": False, "message": "미등록 차량 - 일반 발권"}


@app.post("/api/request-exit")
async def handle_exit_request(request: ExitRequest):
    """AI 카메라(local_server.py)에서 출차 감지 시 호출 - CSV 정산 후 Mock PG 결제"""
    print(f"\n🏢 '{request.car_id}' AI 출차 감지")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    success, message, final_fee = parking_system.process_settlement(request.car_id, now_str)
    print(message)

    plate_location_db.pop(request.car_id.replace(" ", ""), None)

    if not success:
        return {"status": "ERROR", "message": message}

    if final_fee > 0:
        payment_token = encrypt_plate(request.car_id)
        payload = {
            "payment_token": payment_token,
            "fee": int(final_fee),
            "webhook_url": MY_WEBHOOK_URL
        }
        try:
            requests.post(MOCK_PG_URL, json=payload, timeout=5)
        except Exception as e:
            print(f"⚠️ Mock PG 연결 실패: {e}")

    return {"status": "PENDING", "message": f"정산 완료: {message}"}


@app.post("/api/webhook/payment-result")
async def receive_payment_receipt(data: dict):
    """Mock PG에서 결제 완료 후 웹훅 수신"""
    token = data.get("payment_token", "")
    status = data.get("status")
    print(f"\n🔔 [웹훅] 결제 토큰 '{token[:8]}...' 상태: {status}")
    if status == "SUCCESS":
        gate_db[token] = True
        print("🔓 결제 완료 확인 - 차단기 개방 신호 설정")
    return {"message": "영수증 수신 완료"}


@app.get("/api/gate-status")
def get_gate_status(payment_token: str):
    """local_server.py가 폴링: 차단기 개방 여부 확인"""
    open_gate = gate_db.pop(payment_token, False)
    return {"open_gate": open_gate}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
