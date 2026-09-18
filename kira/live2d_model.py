import json, shutil, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
MODEL_DIR=ROOT/"runtime"/"live2d"/"kira"
MODEL_JSON=MODEL_DIR/"kira.model3.json"

def status():
    ok=MODEL_JSON.exists()
    files=[]
    if ok:
        try:
            d=json.loads(MODEL_JSON.read_text(encoding="utf-8"))
            refs=d.get("FileReferences",{})
            files=[refs.get("Moc"),*(refs.get("Textures") or []),refs.get("Physics"),refs.get("DisplayInfo")]
            ok=all(not x or (MODEL_DIR/x).exists() for x in files)
        except Exception: ok=False
    return {"installed":ok,"model":"/live2d/model/kira.model3.json" if ok else None,"directory":str(MODEL_DIR),"files":[x for x in files if x]}

def install_zip(src:Path):
    MODEL_DIR.mkdir(parents=True,exist_ok=True)
    temp=MODEL_DIR/"_import"
    if temp.exists(): shutil.rmtree(temp)
    temp.mkdir()
    with zipfile.ZipFile(src) as z:z.extractall(temp)
    models=list(temp.rglob("*.model3.json"))
    if not models: raise RuntimeError("Archive has no .model3.json")
    source=models[0].parent
    d=json.loads(models[0].read_text(encoding="utf-8")); refs=d.get("FileReferences",{})
    mapping={}
    def cp(rel,new):
        if not rel:return None
        p=source/rel
        if not p.exists():raise RuntimeError(f"Missing Live2D asset: {rel}")
        out=MODEL_DIR/new;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out);mapping[rel]=new;return new
    refs["Moc"]=cp(refs.get("Moc"),"kira.moc3")
    tex=[]
    for i,x in enumerate(refs.get("Textures") or []):tex.append(cp(x,f"textures/texture_{i:02d}.png"))
    refs["Textures"]=tex
    if refs.get("Physics"):refs["Physics"]=cp(refs["Physics"],"kira.physics3.json")
    if refs.get("DisplayInfo"):refs["DisplayInfo"]=cp(refs["DisplayInfo"],"kira.cdi3.json")
    # The supplied model has empty groups. Bind the standard parameters explicitly.
    groups=d.setdefault("Groups",[])
    for name,pid in (("EyeBlink",["ParamEyeLOpen"]),("LipSync",["ParamMouthOpenY"])):
        g=next((g for g in groups if g.get("Name")==name),None)
        if g is None:groups.append({"Target":"Parameter","Name":name,"Ids":pid})
        elif not g.get("Ids"):g["Ids"]=pid
    MODEL_JSON.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
    shutil.rmtree(temp,ignore_errors=True)
    return status()
