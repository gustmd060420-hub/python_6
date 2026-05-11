from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

user_db = {}
parking_db = {}
car_db = {}
card_db = {}
coupon_db = {}


class User(BaseModel):
    user_id: str
    password: str
    name: str = None

class ParkRequest(BaseModel):
    user_id: str
    location: str

class UserIdRequest(BaseModel):
    user_id: str

class CarRequest(BaseModel):
    user_id: str
    plate: str
    model: str
    color: str
    year: str

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

class PlateRequest(BaseModel):
    user_id: str
    plate: str

# 주차장 서버 → 메인 서버 자동 입차/출차용
class AutoParkRequest(BaseModel):
    plate: str          # 번호판 인식 결과 (필수)
    location: str       # 주차장 구역/이름 (필수)
    color: str = None   # 색상 분석 결과 (미구현, 추후 매칭용으로 예약)


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
    """수동 입차 (테스트/관리자용)"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parking_db[req.user_id] = {
        "is_parked": True,
        "location": req.location,
        "parked_time": current_time
    }
    return {"message": req.user_id + "님의 차량이 " + req.location + "에 입차되었습니다."}


@app.post("/parking/auto-enter")
def auto_enter_parking(req: AutoParkRequest):
    """주차장 카메라 서버 → 번호판으로 소유주를 찾아 자동 입차 처리"""
    # car_db 전체에서 번호판 일치하는 사용자 검색
    matched_user_id = None
    for uid, cars in car_db.items():
        for car in cars:
            if car["plate"] == req.plate:
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
    return {
        "message": req.plate + " 차량이 " + req.location + "에 입차 처리되었습니다.",
        "user_id": matched_user_id
    }


@app.post("/parking/auto-exit")
def auto_exit_parking(plate: str):
    """주차장 카메라 서버 → 번호판으로 소유주를 찾아 자동 출차 처리"""
    # car_db 전체에서 번호판 일치하는 사용자 검색
    matched_user_id = None
    for uid, cars in car_db.items():
        for car in cars:
            if car["plate"] == plate:
                matched_user_id = uid
                break
        if matched_user_id:
            break

    if not matched_user_id:
        raise HTTPException(status_code=404, detail="등록된 차량을 찾을 수 없습니다: " + plate)

    if matched_user_id not in parking_db or not parking_db[matched_user_id]["is_parked"]:
        raise HTTPException(status_code=400, detail="주차 중인 차량이 아닙니다.")

    parking_db[matched_user_id]["is_parked"] = False
    return {
        "message": plate + " 차량이 출차 처리되었습니다.",
        "user_id": matched_user_id
    }


@app.post("/parking/exit")
def exit_parking(req: UserIdRequest):
    """수동 출차 (앱 출차 버튼용)"""
    if req.user_id in parking_db and parking_db[req.user_id]["is_parked"]:
        parking_db[req.user_id]["is_parked"] = False
        return {"message": "출차가 완료되었습니다."}
    raise HTTPException(status_code=400, detail="주차된 차량 정보가 없습니다.")


@app.get("/cars")
def get_cars(user_id: str):
    if user_id not in user_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return {"cars": ca