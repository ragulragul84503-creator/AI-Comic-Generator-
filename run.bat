@echo off
title ComicCraft — AI Comic Story Creator
cd /d "%~dp0"
echo ========================================================
echo   ComicCraft — AI Comic Story Creator
echo   Starting FastAPI Server on http://127.0.0.1:8000
echo ========================================================
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
pause
