@echo off
cd /d "%~dp0"
py -3.9 -c "from local_server import run_local_camera; run_local_camera('../../data/media/test_video1.mp4', camera_mode='EXIT')"
pause
