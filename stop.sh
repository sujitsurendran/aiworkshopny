#!/bin/bash
# stop.sh — Stop services started by start.sh (uses .pids file only)
# IMPORTANT: Only kills PIDs recorded in .pids — never uses pkill/killall

echo "Stopping Verizon Customer Credit Platform services..."

if [ -f .pids ]; then
    while IFS= read -r pid; do
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null && echo "  ✓ Stopped PID $pid" || echo "  ✗ PID $pid already stopped"
        fi
    done < .pids
    rm -f .pids
    echo "All services stopped"
else
    echo "No .pids file found — services may not be running or were stopped already"
fi

echo ""
