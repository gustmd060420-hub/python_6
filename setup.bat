@echo off
chcp 65001 > nul
echo 1. 가상환경 만드는 중...
python -m venv venv
echo 2. 영수증(라이브러리) 결제하는 중...
call .\venv\Scripts\activate
pip install -r requirements.txt
echo 세팅 완료! 이제 코딩을 시작하세요.
pause