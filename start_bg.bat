@echo off

chcp 65001 >nul

setlocal



echo 正在通过 WSL 使用 nohup 启动环境疗愈工坊...

cd /d "%~dp0"



where wsl >nul 2>nul

if errorlevel 1 (

    echo 未检测到 WSL，无法执行 Linux nohup 启动。

    echo 请先安装并配置 WSL，或直接在 Linux 服务器上执行 restart.sh。

    pause

    exit /b 1

)



wsl -e bash -lc "cd '/home/zm/my/环境游戏程序/healing-environment' && nohup uv run python main.py >> server_stdout.log 2>> server_stderr.log < /dev/null &"

if errorlevel 1 (

    echo 启动失败，请检查 WSL 环境、uv 是否可用，或查看日志文件。

    pause

    exit /b 1

)



echo 服务已提交到后台。

echo 以后统一使用服务器地址: http://43.167.184.248:6420

echo.

echo 如需重启，建议在 Linux 环境执行: ./restart.sh

echo 日志文件: server_stdout.log / server_stderr.log

pause

