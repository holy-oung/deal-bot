@echo off
title [Deal-Bot] 로컬 24시간 핫딜 봇 (웜업 모드 / 쿠팡 UI 자동화)
echo ==================================================
echo [Deal-Bot] 로컬 24시간 백그라운드 프로세스
echo ==================================================
echo.
echo [안내] 가상 환경 활성화 및 패키지 설치 확인...
python -m pip install -r requirements.txt >nul 2>&1

echo.
echo 봇을 시작합니다. (중지하려면 Ctrl+C를 누르세요)
python main.py

pause
