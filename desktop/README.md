# Kira Studio Desktop

Desktop shell for Kira Studio. It starts Kira Core automatically on a free localhost port and opens Studio in its own native window.

## Arch Linux development

Use Python 3.13. Install GTK/WebKit runtime packages, then:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements-desktop.txt
python desktop/kira_studio.py
```

For a portable binary:

```bash
pyinstaller --clean --noconfirm desktop/KiraStudio.spec
./dist/KiraStudio
```

GitHub Actions produces Windows and Linux artifacts automatically.
