#!/usr/bin/env bash
set -u
echo "=== Kira VTuber / Arch preflight ==="
for c in python curl ollama piper pw-record pw-play wpctl; do
  if command -v "$c" >/dev/null 2>&1; then printf "OK   %s -> %s\n" "$c" "$(command -v "$c")"
  else printf "MISS %s\n" "$c"; fi
done
echo
echo "Audio:"
wpctl status -n 2>/dev/null | sed -n '/Audio/,/Video/p' | head -80 || true
echo
echo "GPU:"
lspci 2>/dev/null | grep -Ei 'VGA|3D|Display' || true
