#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
chmod +x scripts/kira-desktop.sh scripts/install-desktop-entry.sh
mkdir -p "$HOME/.local/share/applications"
cp packaging/kira-vtuber.desktop "$HOME/.local/share/applications/kira-vtuber.desktop"
command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$HOME/.local/share/applications" || true
echo "Kira VTuber launcher installed in the application menu."
