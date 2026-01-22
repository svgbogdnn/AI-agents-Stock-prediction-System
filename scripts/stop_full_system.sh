#!/bin/bash

# Full System Shutdown Script
# Stops all components: Next.js frontend, FastAPI backend, and A2A agents

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                      ║"
echo "║       🛑 Stock Prediction System - Full Stack Shutdown 🛑            ║"
echo "║                                                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Step 1: Stop Next.js Frontend
echo -e "${YELLOW}🎨 Step 1: Stopping Next.js Frontend${NC}"
echo "─────────────────────────────────────────────────────────"

if [ -f "logs/nextjs.pid" ]; then
    NEXTJS_PID=$(cat logs/nextjs.pid)
    if ps -p $NEXTJS_PID > /dev/null 2>&1; then
        echo -e "   Stopping Next.js (PID: $NEXTJS_PID)..."
        kill $NEXTJS_PID 2>/dev/null || true
        sleep 2
        echo -e "${GREEN}   ✅ Next.js stopped${NC}"
    else
        echo -e "${YELLOW}   ⚠️  Next.js process not running${NC}"
    fi
    rm logs/nextjs.pid
fi

# Also kill by port
if lsof -Pi :3001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "   Killing processes on port 3001..."
    lsof -ti:3001 | xargs kill -9 2>/dev/null || true
    echo -e "${GREEN}   ✅ Port 3001 cleared${NC}"
fi

echo ""

# Step 2: Stop FastAPI Backend
echo -e "${YELLOW}🔧 Step 2: Stopping FastAPI Backend${NC}"
echo "─────────────────────────────────────────────────────────"

if [ -f "logs/fastapi.pid" ]; then
    FASTAPI_PID=$(cat logs/fastapi.pid)
    if ps -p $FASTAPI_PID > /dev/null 2>&1; then
        echo -e "   Stopping FastAPI (PID: $FASTAPI_PID)..."
        kill $FASTAPI_PID 2>/dev/null || true
        sleep 2
        echo -e "${GREEN}   ✅ FastAPI stopped${NC}"
    else
        echo -e "${YELLOW}   ⚠️  FastAPI process not running${NC}"
    fi
    rm logs/fastapi.pid
fi

# Also kill by port
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "   Killing processes on port 8000..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    echo -e "${GREEN}   ✅ Port 8000 cleared${NC}"
fi

echo ""

# Step 3: Stop A2A Agents
echo -e "${YELLOW}📡 Step 3: Stopping A2A Agents${NC}"
echo "─────────────────────────────────────────────────────────"

./scripts/stop_all_agents.sh

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                      ║"
echo "║                   ✅ System Stopped Successfully ✅                   ║"
echo "║                                                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}All components have been shut down:${NC}"
echo "   ✅ Next.js Frontend (port 3001)"
echo "   ✅ FastAPI Backend (port 8000)"
echo "   ✅ A2A Agents (ports 8001-8006)"
echo ""
echo -e "${YELLOW}To start the system again:${NC}"
echo "   ./scripts/start_full_system.sh"
echo ""

