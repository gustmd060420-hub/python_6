from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import uvicorn

app = FastAPI()

# 가상 데이터베이스
user_db = {}
parking_db = {}


class User(BaseModel):
    user_id: str
    password: str
    name: str = None


class ParkRequest(BaseModel):
    user_id: str
    location: str


class UserIdRequest(BaseModel):
    user_id: str


@app.post("/signup")
def signup(user: User):
    if user.user_id in user_db:
        raise HTTPException(status_code=400, detail="이미 존재하는 아이디입니다.")
    user_db[user.user_id] = {"password": user.password, "name": user.name}
    return {"message": "회원가입 완료"}


@app.post("/login")
def login(user: User):
    if user.user_id not in user_db or user_db[user.user_id]["password"] != user.password:
        raise HTTPException(status_code=401, detail="정보가 일치하지 않습니다.")
    return {"message": "로그인 성공", "name": user_db[user.user_id]["name"]}


@app.get("/parking/status")
def get_parking_status(user_id: str):
    if user_id in parking_db and parking_db[user_id]["is_parked"]:
        return {
            "is_parked": True,
            "location": parking_db[user_id]["location"],
            "parked_time": parking_db[user_id]["parked_time"],
            "fee": "0원"
        }
    return {"is_parked": False}


@app.post("/parking/enter")
def enter_parking(req: ParkRequest):
    # 입차 순간의 시간을 YYYY-MM-DD HH:MM:SS 형태로 저장
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    parking_db[req.user_id] = {
        "is_parked": True,
        "location": req.location,
        "parked_time": current_time
    }
    return {"message": f"{req.user_id}님의 차량이 {req.location}에 입차되었습니다."}


@app.post("/parking/exit")
def exit_parking(req: UserIdRequest):
    if req.user_id in parking_db and parking_db[req.user_id]["is_parked"]:
        # 출차 시 주차 상태를 False로 변경
        parking_db[req.user_id]["is_parked"] = False
        return
    else:
        raise HTTPException(status_code=400, detail="주차된 차량 정보가 없습니다.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)