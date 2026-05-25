import os
import sys

VIDEO_ENTRY = "../../data/media/test_video1.mp4"
VIDEO_EXIT  = "../../data/media/test_video1.mp4"

def main():
    print("=" * 40)
    print("   주차장 카메라 실행기")
    print("=" * 40)
    print("1. 입차 카메라 실행")
    print("2. 출차 카메라 실행")
    print("=" * 40)

    choice = input("선택 (1 or 2): ").strip()

    if choice == "1":
        from local_server import run_local_camera
        run_local_camera(VIDEO_ENTRY, camera_mode="ENTRY")
    elif choice == "2":
        from local_server import run_local_camera
        run_local_camera(VIDEO_EXIT, camera_mode="EXIT")
    else:
        print("잘못된 입력입니다. 1 또는 2를 입력하세요.")
        sys.exit(1)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
