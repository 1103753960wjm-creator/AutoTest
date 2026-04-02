#!/bin/bash

# TestHub 一键启动脚本 (适合 Git Bash / WSL 环境)

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}正在初始化 TestHub 服务...${NC}"

# 1. 端口清理 (8000 和 3000)
echo -e "${YELLOW}检查并清理端口占用 (8000, 3000)...${NC}"
# Windows Git Bash 下使用 taskkill
for port in 8000 3000; do
    pid=$(netstat -ano | grep ":$port" | grep "LISTENING" | awk '{print $5}' | head -n 1)
    if [ ! -z "$pid" ]; then
        echo -e "${RED}发现端口 $port 被进程 $pid 占用，正在关闭...${NC}"
        taskkill -F -PID $pid 2>/dev/null || kill -9 $pid 2>/dev/null
    fi
done

# 2. 启动后端 (Django)
echo -e "${GREEN}正在启动后端服务 (Django)...${NC}"
# 设置环境变量 (根据之前的经验，DEBUG 需要处理)
export DEBUG=""
# 使用虚拟环境的 Python
./venv/Scripts/python.exe manage.py runserver 0.0.0.0:8000 > backend_start.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}后端服务已在后台启动 (PID: $BACKEND_PID)，日志输出至 backend_start.log${NC}"

# 3. 启动前端 (Vite)
echo -e "${GREEN}正在启动前端服务 (Vite/Vue)...${NC}"
cd frontend
npm run dev

# 脚本退出时尝试关闭后端进程 (如果前端退出)
# trap "kill $BACKEND_PID" EXIT
