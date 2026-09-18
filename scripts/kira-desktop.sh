#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p runtime
LOG="runtime/kira.log"

if ! pgrep -x ollama >/dev/null 2>&1 && command -v ollama >/dev/null 2>&1; then
  nohup ollama serve >>"$LOG" 2>&1 &
  sleep 2
fi

source .venv/bin/activate
python -m kira.main >>"$LOG" 2>&1 &
CORE_PID=$!

cleanup(){ kill "$CORE_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

for _ in {1..30}; do
  if curl -fsS http://127.0.0.1:8765/health >/dev/null 2>&1; then break; fi
  sleep .25
done

if command -v chromium >/dev/null 2>&1; then
  chromium --app=http://127.0.0.1:8765/studio --class=KiraStudio
elif command -v google-chrome-stable >/dev/null 2>&1; then
  google-chrome-stable --app=http://127.0.0.1:8765/studio
elif command -v firefox >/dev/null 2>&1; then
  firefox --new-window http://127.0.0.1:8765/studio
else
  echo "Open http://127.0.0.1:8765/studio"
  wait "$CORE_PID"
fi
