@echo off
chcp 65001 >nul
echo 正在后台启动环境疗愈工坊服务...
cd /d "%~dp0"
start "" /B .venv\Scripts\python.exe main.py > server.log 2>&1
echo 服务已在后台启动！
echo 日志文件: %~dp0server.log
echo 访问地址: http://localhost:8080
echo.
echo 如需停止服务，请运行 stop_bg.bat
pause
