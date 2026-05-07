from fastapi import FastAPI, BackgroundTasks
import requests
import asyncio
import uvicorn

app = FastAPI(title="가짜 네이버페이 서버")

async def process_payment(payment_token: str, fee: int, webhook_url: str):
    # 💡 [보안 패치] 차량 번호 대신 익명 토큰의 앞부분만 출력합니다.
    print(f"💸 [네이버페이] 익명 결제토큰 '{payment_token[:8]}...' {fee}원 승인 대기 중... (3초 소요)")
    await asyncio.sleep(3)  
    
    print(f"✅ [네이버페이] 결제 승인 완료! 중앙 서버로 영수증 발송 중...")
    receipt_data = {"payment_token": payment_token, "status": "SUCCESS", "paid_amount": fee}
    try:
        requests.post(webhook_url, json=receipt_data)
    except Exception as e:
        print(f"❌ 웹훅 발송 실패: {e}")

@app.post("/api/pay")
async def request_payment(data: dict, background_tasks: BackgroundTasks):
    # car_id를 지우고 payment_token을 받습니다.
    payment_token = data.get("payment_token")
    fee = data.get("fee")
    webhook_url = data.get("webhook_url")
    
    background_tasks.add_task(process_payment, payment_token, fee, webhook_url)
    return {"message": "네이버페이 결제 요청이 접수되었습니다."}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)