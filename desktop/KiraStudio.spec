# PyInstaller specification for Kira Studio Desktop
from PyInstaller.utils.hooks import collect_submodules
hiddenimports=collect_submodules("uvicorn")+collect_submodules("pydantic")+collect_submodules("fastapi")
a=Analysis(["desktop/kira_studio.py"],pathex=["."],binaries=[],datas=[("web","web")],hiddenimports=hiddenimports)
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,a.binaries,a.datas,[],name="KiraStudio",console=False,debug=False,strip=False,upx=False)
