#!/bin/bash
# 环境疗愈工坊 - 启动脚本
# 用法: ./restart.sh
# 访问: http://43.167.184.248:6420

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# 杀掉旧进程
pkill -9 -f "python main.py" 2>/dev/null
fuser -k 6420/tcp 2>/dev/null
sleep 1

# 启动（前台运行重定向日志，脱离终端）
nohup uv run python main.py >> server_stdout.log 2>>server_stderr.log &
PID=$!
echo "启动中，PID: $PID"
disown $PID

# 等待就绪
for i in $(seq 1 20); do
    sleep 1
    if ss -tlnp | grep -q 6420; then
        echo "✓ 服务已就绪"
        echo "  以后统一使用服务器地址: http://43.167.184.248:6420"
        exit 0
    fi
done

echo "✗ 启动超时，查看日志:"
tail -20 server_stderr.log
exit 1
