#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

PYTHON="${PYTHON:-python3.13}"
command -v "$PYTHON" >/dev/null || { echo "Нужен Python 3.13. На Arch установи пакет python313 из AUR."; exit 1; }

echo "== Kira Studio: Python окружение =="
"$PYTHON" -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements-desktop.txt
[ -f .env ] || cp .env.example .env

echo "== Проверка внешних компонентов =="
for x in ollama piper pw-play pw-record; do
  if command -v "$x" >/dev/null; then echo "✓ $x"; else echo "! $x не найден"; fi
done

if command -v ollama >/dev/null; then
  (ollama serve >/tmp/kira-ollama.log 2>&1 &) || true
  sleep 2
  echo "== Загрузка локальной LLM =="
  ollama pull qwen3:4b || echo "! Модель не скачалась. Повтори позже из Kira Studio."
fi

echo "== Проверка Kira Core =="
python -m compileall -q kira
python -c "import kira.main; print('✓ Kira Core готов')"
echo
echo "Готово. Запуск: source .venv/bin/activate && python desktop/kira_studio.py"
