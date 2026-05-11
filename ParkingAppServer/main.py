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

class PlateRequest(BaseModel):
    user_id: str
    plate: str


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
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parking_db[req.user_id] = {
        "is_parked": True,
        "location": req.location,
        "parked_time": current_time
    }
    return {"message": req.user_id + "님의 차량이 " + req.location + "에 입차되었습니다."}


@app.post("/parking/exit")
def exit_parking(req: UserIdRequest):
    if req.user_id in parking_db and parking_db[req.user_id]["is_parked"]:
        parking_db[req.user_id]["is_parked"] = False
        return {"message": "출차가 완료되었습니다."}
    raise HTTPException(status_code=400, detail="주차된 차량 정보가 없습니다.")


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
def delete_card(req: CardRequest):
    if req.user_id not in user_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    cards = card_db.get(req.user_id, [])
    new_cards = [c for c in cards if c["card_number"] != req.card_number]
    if len(new_cards) == len(cards):
        raise HTTPException(status_code=404, detail="해당 카드를 찾을 수 없습니다.")
    card_db[req.user_id] = new_cards
    return {"message": "카드가 삭제되었습니다."}


@app.get("/coupons")
def get_coupons(user_id: str):
    if user_id not in user_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return {"coupons": coupon_db.get(user_id, [])}
