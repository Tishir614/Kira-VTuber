"""Kira Studio Desktop launcher for Windows and Linux."""
from __future__ import annotations
import os, socket, subprocess, sys, threading, time, shutil
from pathlib import Path
from urllib.request import urlopen
import webview
try:
    import pystray
    from PIL import Image,ImageDraw
except Exception:
    pystray=None

APP_NAME="Kira Studio"
HOST="127.0.0.1"

def data_root()->Path:
    if sys.platform.startswith("win"):
        base=Path(os.environ.get("LOCALAPPDATA",Path.home()/"AppData"/"Local"))
    else:
        base=Path(os.environ.get("XDG_DATA_HOME",Path.home()/".local"/"share"))
    p=base/"KiraStudio";p.mkdir(parents=True,exist_ok=True);return p

def resource_root()->Path:
    if getattr(sys,"frozen",False):
        return Path(getattr(sys,"_MEIPASS",Path(sys.executable).parent))
    return Path(__file__).resolve().parent.parent

def free_port()->int:
    with socket.socket() as s:
        s.bind((HOST,0)); return int(s.getsockname()[1])

def wait_health(port:int, timeout:float=30)->bool:
    end=time.time()+timeout
    while time.time()<end:
        try:
            with urlopen(f"http://{HOST}:{port}/health",timeout=1) as r:
                if r.status==200:return True
        except Exception: time.sleep(.25)
    return False

class Desktop:
    def __init__(self):
        self.proc=None; self.port=free_port(); self.window=None; self.tray=None
    def start_core(self):
        env=os.environ.copy(); env["KIRA_HOST"]=HOST; env["KIRA_PORT"]=str(self.port)
        root=resource_root()
        data=data_root();env["KIRA_DATA_DIR"]=str(data);env["KIRA_DESKTOP_PORT"]=str(self.port)
        # Keep writable runtime/settings outside the PyInstaller bundle.
        os.chdir(data)
        if getattr(sys,"frozen",False):
            cmd=[sys.executable,"--desktop-core",str(self.port)]
        else:
            cmd=[sys.executable,"-m","uvicorn","kira.main:app","--host",HOST,"--port",str(self.port)]
        self.proc=subprocess.Popen(cmd,cwd=str(root),env=env)
        return wait_health(self.port)
    def show(self):
        if self.window:
            try:self.window.show()
            except Exception:pass
    def hide(self):
        if self.window:
            try:self.window.hide()
            except Exception:pass
    def tray_icon(self):
        if not pystray:return
        img=Image.new("RGBA",(64,64),(18,10,30,255));d=ImageDraw.Draw(img);d.ellipse((9,9,55,55),fill=(150,80,220,255));d.text((24,19),"K",fill="white")
        def quit_app(icon,item):
            icon.stop();self.stop()
            if self.window:
                try:self.window.destroy()
                except Exception:pass
        self.tray=pystray.Icon("KiraStudio",img,"Kira Studio",pystray.Menu(pystray.MenuItem("Открыть Kira Studio",lambda i,x:self.show()),pystray.MenuItem("Скрыть",lambda i,x:self.hide()),pystray.MenuItem("Выход",quit_app)))
        threading.Thread(target=self.tray.run,daemon=True).start()
    def stop(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:self.proc.kill()

def run_core_mode(port:int):
    import uvicorn
    uvicorn.run("kira.main:app",host=HOST,port=port,log_level="warning")

def main():
    if "--desktop-core" in sys.argv:
        i=sys.argv.index("--desktop-core"); run_core_mode(int(sys.argv[i+1])); return
    app=Desktop()
    if not app.start_core():
        app.stop()
        webview.create_window(APP_NAME,"data:text/html,<body style='background:%23100b18;color:white;font-family:sans-serif;padding:32px'><h2>Kira Core не запустился</h2><p>Проверь зависимости и журнал запуска.</p></body>",width=900,height=600)
        webview.start(); return
    window=webview.create_window(APP_NAME,f"http://{HOST}:{app.port}/studio",width=1280,height=820,min_size=(900,600))
    app.window=window
    try:webview.start(lambda:app.tray_icon())
    finally:
        if app.tray:
            try:app.tray.stop()
            except Exception:pass
        app.stop()

if __name__=="__main__": main()
