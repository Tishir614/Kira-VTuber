#!/usr/bin/env bash
set -euo pipefail
BIN="${1:-dist/KiraStudio}"
test -f "$BIN" || { echo "KiraStudio binary not found: $BIN"; exit 1; }
mkdir -p "$HOME/.local/bin" "$HOME/.local/share/applications" "$HOME/.config/autostart"
install -m755 "$BIN" "$HOME/.local/bin/KiraStudio"
install -m644 desktop/linux/kira-studio.desktop "$HOME/.local/share/applications/kira-studio.desktop"
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true\necho "Kira Studio installed. Run: KiraStudio"
