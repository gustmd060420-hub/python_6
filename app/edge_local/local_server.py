import cv2
import hashlib
import time
import requests
from datetime import datetime
from ai_pipeline import RealTimePlateReader, LicensePlateEnsembler

CENTRAL_SERVER = "http://127.0.0.1:8000"
PARKING_LOT_ID = "INHA_UNIV_01"
SALT = "NAVER_AUTOPAY_SECRET_2026"

MAX_RETRIES = 3          # 번호판 인식 실패 시 재시도 횟수
GATE_POLL_INTERVAL = 1   # 차단기 폴링 간격 (초)
GATE_POLL_MAX = 15       # 최대 폴링 횟수 (15초 대기)


def encrypt_plate(plate: str) -> str:
    return hashlib.sha256((plate + SALT).encode()).hexdigest()


def _recognize_plate(video_path, ai_reader, camera_mode):
    """영상/웹캠에서 30프레임 앙상블로 번호판 인식. 성공 시 (plate, token), 실패 시 (None, None)"""
    ensembler = LicensePlateEnsembler(confidence_threshold=0.3)
    cap = cv2.VideoCapture(video_path)
    valid_frames = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        plate_text, confidence = ai_reader.process_frame(frame)
        if plate_text:
            ensembler.add_frame_result(plate_text, confidence)
            valid_frames += 1
            print(f"[{camera_mode}][{valid_frames}/30] {plate_text} (신뢰도: {confidence:.2f})")
        if valid_frames >= 30:
            break

    cap.release()
    final_plate, _ = ensembler.get_final_result()
    if not final_plate:
        return None, None
    return final_plate, encrypt_plate(final_plate)


def _poll_gate(payment_token: str) -> bool:
    """차단기 개방 신호 폴링. 개방되면 True 반환"""
    print("결제 완료 대기 중...", end="", flush=True)
    for _ in range(GATE_POLL_MAX):
        time.sleep(GATE_POLL_INTERVAL)
        try:
            resp = requests.get(f"{CENTRAL_SERVER}/api/gate-status",
                                params={"payment_token": payment_token}, timeout=3)
            if resp.json().get("open_gate"):
                print(" 차단기 개방!")
                return True
        except Exception:
            pass
        print(".", end="", flush=True)
    print(" 타임아웃")
    return False


def run_local_camera(video_path, camera_mode="ENTRY"):
    print(f"\n[{camera_mode}] 카메라 시작: {video_path}")

    ai_reader = RealTimePlateReader('../../models/best.pt')
    final_plate = None
    payment_token = None

    for attempt in range(1, MAX_RETRIES + 1):
        if attempt > 1:
            print(f"번호판 재인식 시도 {attempt}/{MAX_RETRIES}...")
        final_plate, payment_token = _recognize_plate(video_path, ai_reader, camera_mode)
        if final_plate:
            break

    if not final_plate:
        print(f"번호판 인식 실패 ({MAX_RETRIES}회 시도). 차단기 유지.")
        return

    print(f"\n[AI 최종 판독] {final_plate}")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if camera_mode == "ENTRY":
        try:
            resp = requests.post(f"{CENTRAL_SERVER}/api/entry", json={
                "plate_number": final_plate,
                "parking_lot_id": PARKING_LOT_ID,
                "entry_time": now_str
            })
            result = resp.json()
            print("중앙 서버 응답:", result)
            if result.get("open_gate"):
                print("🔓 차단기 개방")
            else:
                print("❌ 미등록 차량 - 일반 발권")
        except Exception as e:
            print(f"중앙 서버 통신 실패: {e}")

    elif camera_mode == "EXIT":
        try:
            resp = requests.post(f"{CENTRAL_SERVER}/api/request-exit", json={
                "car_id": final_plate,
                "fee": 0  # 중앙 서버가 CSV에서 직접 계산
            })
            result = resp.json()
            print("중앙 서버 응답:", result)

            if result.get("status") == "ERROR":
                print("❌ 출차 처리 실패:", result.get("message"))
                return

            # 결제 완료 후 차단기 개방 폴링
            gate_opened = _poll_gate(payment_token)
            if not gate_opened:
                print("⚠️ 결제 확인 타임아웃. 수동 개방 필요.")

        except Exception as e:
            print(f"중앙 서버 통신 실패: {e}")


if __name__ == "__main__":
    run_local_camera("../../data/media/test_video1.mp4", camera_mode="ENTRY")
    # run_local_camera("../../data/media/test_video1.mp4", camera_mode="EXIT")
    # run_local_camera("../../data/media/test_video2.mp4", camera_mode="ENTRY")
    # run_local_camera("../../data/media/test_video2.mp4", camera_mode="EXIT")
