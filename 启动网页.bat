@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在启动生活助手平台...
echo 启动后浏览器访问: http://127.0.0.1:8000/
python server.py
pause
