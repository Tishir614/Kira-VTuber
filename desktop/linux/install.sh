#!/usr/bin/env bash
set -euo pipefail
BIN="${1:-dist/KiraStudio}"
test -f "$BIN" || { echo "KiraStudio binary not found: $BIN"; exit 1; }
mkdir -p "$HOME/.local/bin" "$HOME/.local/share/applications"
install -m755 "$BIN" "$HOME/.local/bin/KiraStudio"
install -m644 desktop/linux/kira-studio.desktop "$HOME/.local/share/applications/kira-studio.desktop"
echo "Kira Studio installed. Run: KiraStudio"
