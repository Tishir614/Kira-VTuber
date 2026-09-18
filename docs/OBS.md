# OBS overlay

Kira exposes a localhost-only browser overlay at `/overlay`.

In OBS add a Browser Source and point it to:

`http://127.0.0.1:8765/overlay`

The page background is transparent. It is intended for subtitles/status now and for the Live2D renderer later. Keep Kira Core bound to localhost unless you intentionally configure network access.
