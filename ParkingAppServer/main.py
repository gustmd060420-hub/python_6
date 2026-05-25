import uvicorn
import hashlib
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="주차장 중앙 메인 서버")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 🔒 보안 / 결제 설정
# ==========================================
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

# ==========================================
# 💾 인메모리 DB
# ==========================================
user_db = {}
parking_db = {}
car_db = {}
card_db = {}
coupon_db = {}

# 결제 대기 중인 토큰 → {user_id, fee} 매핑 (웹훅 수신 시 parking_db + 이력 업데이트용)
pending_payments = {}

# 주차 이용 이력 (user_id → list of records)
parking_history = {}

coupon_code_db = {
    "PYPASS30":  {"title": "30분 무료 주차", "description": "Py-Pass 전용 혜택",  "expires_at": "2025-12-31"},
    "PYPASS1H":  {"title": "1시간 무료 주차", "description": "특별 할인 쿠폰",     "expires_at": "2025-12-31"},
    "WELCOME10": {"title": "10% 할인 쿠폰",  "description": "신규 가입 혜택",      "expires_at": "2025-12-31"},
}

# ==========================================
# 📦 요청 모델
# ==========================================
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
    year: str = ""

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

class PlateRequest(BaseModel):
    user_id: str
    plate: str

class UpdateNameRequest(BaseModel):
    user_id: str
    name: str

class SetDefaultCarRequest(BaseModel):
    user_id: str
    plate: str

class AutoParkRequest(BaseModel):
    plate: str
    location: str
    color: str = None

# 주차장 로컬 서버 연동용 모델
class EntryRequest(BaseModel):
    plate_number: str
    parking_lot_id: str
    entry_time: str

class ExitRequest(BaseModel):
    car_id: str
    fee: int

# ==========================================
# 👤 회원 관리
# ==========================================
@app.post("/signup")
def signup(user: User):
    if user.user_id in user_db:
        raise HTTPException(status_code=400, detail="이미 존재하는 아이디입니다.")
    user_db[user.user_id] = {"password": user.password, "name": user.name}
    car_db[user.user_id] = []
    card_db[user.user_id] = []
    coupon_db[user.user_id] = []
    return {"message": "회원가입 완료"}


@app.post("/login")
def login(user: User):
    if user.user_id not in user_db or user_db[user.user_id]["password"] != user.password:
        raise HTTPException(status_code=401, detail="정보가 일치하지 않습니다.")
    car_db.setdefault(user.user_id, [])
    card_db.setdefault(user.user_id, [])
    coupon_db.setdefault(user.user_id, [])
    return {"message": "로그인 성공", "name": user_db[user.user_id]["name"]}


@app.get("/user/info")
def get_user_info(user_id: str):
    if user_id not in user_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return {"user_id": user_id, "name": user_db[user_id]["name"]}


@app.post("/user/update-name")
def update_user_name(req: UpdateNameRequest):
    if req.user_id not in user_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    user_db[req.user_id]["name"] = req.name
    return {"message": "이름이 수정되었습니다."}


@app.post("/user/delete")
def delete_user(req: UserIdRequest):
    if req.user_id not in user_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    user_db.pop(req.user_id, None)
    car_db.pop(req.user_id, None)
    card_db.pop(req.user_id, None)
    coupon_db.pop(req.user_id, None)
    parking_db.pop(req.user_id, None)
    return {"message": "회원 탈퇴가 완료되었습니다."}

# ==========================================
# 🅿️ 주차 관리 (앱 연동)
# ==========================================
@app.get("/parking/status")
def get_parking_status(user_id: str):
    if user_id in parking_db and parking_db[user_id]["is_parked"]:
        entry = parking_db[user_id]
        try:
            entry_dt = datetime.strptime(entry["parked_time"], "%Y-%m-%d %H:%M:%S")
            elapsed_minutes = int((datetime.now() - entry_dt).total_seconds() / 60)
            billable_minutes = max(0, elapsed_minutes - 30)
            fee_str = str(billable_minutes * 100) + "원"
        except Exception:
            fee_str = "계산 불가"
        return {
            "is_parked": True,
            "location": entry["location"],
            "parked_time": entry["parked_time"],
            "fee": fee_str
        }
    return {"is_parked": False}


@app.post("/parking/enter")
def enter_parking(req: ParkRequest):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parking_db[req.user_id] = {
        "is_parked": True,
        "location": req.location,
        "parked_time": current_time
    }
    return {"message": req.user_id + "님의 차량이 " + req.location + "에 입차되었습니다."}


@app.post("/parking/exit")
def exit_parking(req: UserIdRequest):
    """
    앱에서 출차 요청 시 호출.
    1. 주차 기록 확인 및 요금 계산
    2. 등록된 차량 번호로 네이버페이 결제 요청
    3. 웹훅(/api/webhook/payment-result)에서 SUCCESS 수신 시 자동 출차 처리
    """
    if req.user_id not in parking_db or not parking_db[req.user_id]["is_parked"]:
        raise HTTPException(status_code=400, detail="주차된 차량 정보가 없습니다.")

    # 요금 계산
    entry = parking_db[req.user_id]
    try:
        entry_dt = datetime.strptime(entry["parked_time"], "%Y-%m-%d %H:%M:%S")
        elapsed_minutes = int((datetime.now() - entry_dt).total_seconds() / 60)
        fee = max(0, elapsed_minutes - 30) * 100
    except Exception:
        fee = 0

    # 등록된 기본 차량 번호 조회
    cars = car_db.get(req.user_id, [])
    default_car = next((c for c in cars if c.get("is_default")), cars[0] if cars else None)

    if not default_car:
        raise HTTPException(status_code=400, detail="등록된 차량이 없습니다. 차량을 먼저 등록해주세요.")

    plate = default_car["plate"]
    payment_token = encrypt_plate(plate)

    # 결제 대기 매핑 등록
    pending_payments[payment_token] = {"user_id": req.user_id, "fee": fee}

    payload = {
        "payment_token": payment_token,
        "fee": fee,
        "webhook_url": MY_WEBHOOK_URL
    }

    try:
        requests.post(NAVER_PAY_URL, json=payload, timeout=5)
        print(f"📱 [앱 출차 요청] '{req.user_id}' / 차량: {plate} / 요금: {fee}원 → 네이버페이 요청 완료")
    except Exception:
        # 결제 서버 연결 실패 시 매핑 제거
        pending_payments.pop(payment_token, None)
        return {"status": "ERROR", "message": "결제 서버 연결 실패"}

    return {"status": "PENDING", "message": f"결제 요청 완료. 요금: {fee}원. 결제 확인 후 출차 처리됩니다."}


@app.post("/parking/auto-enter")
def auto_enter_parking(req: AutoParkRequest):
    normalized_plate = req.plate.replace(" ", "")
    matched_user_id = None
    for uid, cars in car_db.items():
        for car in cars:
            if car["plate"].replace(" ", "") == normalized_plate:
                matched_user_id = uid
                break
        if matched_user_id:
            break

    if not matched_user_id:
        raise HTTPException(status_code=404, detail="등록된 차량을 찾을 수 없습니다: " + req.plate)

    if matched_user_id in parking_db and parking_db[matched_user_id]["is_parked"]:
        raise HTTPException(status_code=400, detail="이미 주차 중인 차량입니다.")

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parking_db[matched_user_id] = {
        "is_parked": True,
        "location": req.location,
        "parked_time": current_time
    }
    # 이력 기록 시작
    parking_history.setdefault(matched_user_id, []).append({
        "location": req.location,
        "entry_time": current_time,
        "exit_time": None,
        "fee": None
    })
    return {
        "message": req.plate + " 차량이 " + req.location + "에 입차 처리되었습니다.",
        "user_id": matched_user_id
    }


@app.post("/parking/auto-exit")
def auto_exit_parking(plate: str):
    normalized_plate = plate.replace(" ", "")
    matched_user_id = None
    for uid, cars in car_db.items():
        for car in cars:
            if car["plate"].replace(" ", "") == normalized_plate:
                matched_user_id = uid
                break
        if matched_user_id:
            break

    if not matched_user_id:
        raise HTTPException(status_code=404, detail="등록된 차량을 찾을 수 없습니다: " + plate)

    if matched_user_id not in parking_db or not parking_db[matched_user_id]["is_parked"]:
        raise HTTPException(status_code=400, detail="주차 중인 차량이 아닙니다.")

    parking_db[matched_user_id]["is_parked"] = False
    # 이력 기록 완료 (요금 없는 수동 출차)
    for record in reversed(parking_history.get(matched_user_id, [])):
        if record["exit_time"] is None:
            record["exit_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            record["fee"] = "수동 출차"
            break
    return {
        "message": plate + " 차량이 출차 처리되었습니다.",
        "user_id": matched_user_id
    }

# ==========================================
# 🏢 주차장 로컬 서버 연동 API
# ==========================================
@app.post("/api/entry")
async def handle_vehicle_entry(request: EntryRequest):
    print(f"\n🏢 [중앙 서버] [{request.parking_lot_id}] 차량 입차 데이터 수신 완료!")
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
    """주차장 로컬 서버(키오스크/차단기)에서 직접 출차 요청 시 호출"""
    print(f"\n🏢 [중앙 서버] '{request.car_id}' 출차 요청 수신. 정산 요금: {request.fee}원")
    payment_token = encrypt_plate(request.car_id)
    print(f"🔒 [보안] 결제용 익명 토큰으로 변환 완료: {payment_token[:15]}...")

    # 웹훅 수신 시 parking_db 업데이트를 위해 매핑 등록
    normalized = request.car_id.replace(" ", "")
    for uid, cars in car_db.items():
        for car in cars:
            if car["plate"].replace(" ", "") == normalized:
                pending_payments[payment_token] = {"user_id": uid, "fee": request.fee}
                break

    payload = {
        "payment_token": payment_token,
        "fee": request.fee,
        "webhook_url": MY_WEBHOOK_URL
    }
    try:
        requests.post(NAVER_PAY_URL, json=payload, timeout=5)
    except Exception:
        return {"status": "ERROR", "message": "결제 서버 연결 실패"}

    return {"status": "PENDING", "message": "결제 진행 중. 차단기 대기."}


@app.post("/api/webhook/payment-result")
async def receive_payment_receipt(data: dict):
    """네이버페이 결제 결과 수신 → SUCCESS 시 parking_db 자동 출차 처리"""
    payment_token = data.get("payment_token", "")
    status = data.get("status")

    print(f"\n🔔 [웹훅 수신] 결제 토큰 '{payment_token[:8]}...' 상태: {status}")

    if status == "SUCCESS":
        info = pending_payments.pop(payment_token, None)
        user_id = info["user_id"] if info else None
        fee = info["fee"] if info else None
        if user_id and user_id in parking_db:
            parking_db[user_id]["is_parked"] = False
            # 이력 기록 완료
            for record in reversed(parking_history.get(user_id, [])):
                if record["exit_time"] is None:
                    record["exit_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    record["fee"] = str(fee) + "원" if fee is not None else "알 수 없음"
                    break
            print(f"🔓 결제 확인 완료 → '{user_id}' 출차 처리 및 차단기 개방")
        else:
            print("⚠️ 결제 성공이나 매핑된 user_id 없음 (로컬 서버 직접 요청)")

    return {"message": "영수증 수신 완료"}

# ==========================================
# 🚗 차량 관리
# ==========================================
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
    return {"message": "차량이 등록되었습니다."}


@app.post("/cars/set-default")
def set_default_car(req: SetDefaultCarRequest):
    if req.user_id not in user_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    cars = car_db.get(req.user_id, [])
    normalized = req.plate.replace(" ", "")
    found = False
    for car in cars:
        if car["plate"].replace(" ", "") == normalized:
            car["is_default"] = True
            found = True
        else:
            car["is_default"] = False
    if not found:
        raise HTTPException(status_code=404, detail="해당 차량을 찾을 수 없습니다.")
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

# ==========================================
# 💳 카드 관리
# ==========================================
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

# ==========================================
# 🎟️ 쿠폰 관리
# ==========================================
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


# ==========================================
# 📋 주차 이용 이력
# ==========================================
@app.get("/parking/history")
def get_parking_history(user_id: str):
    if user_id not in user_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    history = parking_history.get(user_id, [])
    return {"history": list(reversed(history))}  # 최신순 반환


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
