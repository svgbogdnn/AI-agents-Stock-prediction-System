#!/bin/bash
# Stop all A2A agent servers

echo "🛑 Stopping Stock Prediction System - All Agents"
echo "================================================"

# Get the project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Stop agents using PID files
if [ -d ".pids" ]; then
    for pid_file in .pids/*.pid; do
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            agent_name=$(basename "$pid_file" .pid)
            
            if ps -p $pid > /dev/null 2>&1; then
                echo "  → Stopping $agent_name (PID: $pid)..."
                kill $pid
            else
                echo "  ℹ️  $agent_name already stopped"
            fi
            
            rm "$pid_file"
        fi
    done
fi

# Fallback: Kill by process name pattern
echo ""
echo "Cleaning up any remaining agent processes..."
pkill -f "agents/.*_server.py" 2>/dev/null

# Wait a moment
sleep 2

# Verify all stopped
echo ""
echo "Verifying shutdown..."
for port in 8001 8002 8003 8004 8005 8006; do
    if lsof -i :$port > /dev/null 2>&1; then
        echo "  ⚠️  Port $port still in use"
    else
        echo "  ✅ Port $port freed"
    fi
done

echo ""
echo "================================================"
echo "✅ All agents stopped"
echo "================================================"

