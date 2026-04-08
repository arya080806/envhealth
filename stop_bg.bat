@echo off
chcp 65001 >nul
echo 正在停止环境疗愈工坊服务...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
    echo 已终止进程 PID: %%a
)
echo 服务已停止。
pause
