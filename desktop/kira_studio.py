"""Kira Studio Desktop launcher for Windows and Linux."""
from __future__ import annotations
import os, socket, subprocess, sys, threading, time
from pathlib import Path
from urllib.request import urlopen
import webview

APP_NAME="Kira Studio"
HOST="127.0.0.1"

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
        self.proc=None; self.port=free_port()
    def start_core(self):
        env=os.environ.copy(); env["KIRA_HOST"]=HOST; env["KIRA_PORT"]=str(self.port)
        root=resource_root()
        if getattr(sys,"frozen",False):
            cmd=[sys.executable,"--desktop-core",str(self.port)]
        else:
            cmd=[sys.executable,"-m","uvicorn","kira.main:app","--host",HOST,"--port",str(self.port)]
        self.proc=subprocess.Popen(cmd,cwd=str(root),env=env)
        return wait_health(self.port)
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
    try:webview.start()
    finally:app.stop()

if __name__=="__main__": main()
