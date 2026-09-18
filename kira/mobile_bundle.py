import io,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
SAFE_FILES=["runtime/settings.json","runtime/memory.json","runtime/twitch_oauth.json","runtime/youtube_oauth.json"]
def export_bundle(include_secrets=False):
    out=io.BytesIO()
    with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("bundle.json",json.dumps({"format":"kira-mobile-bundle","version":1},indent=2))
        for rel in SAFE_FILES:
            p=ROOT/rel
            if not p.exists():continue
            if not include_secrets and ("oauth" in rel or rel.endswith("settings.json")):
                if rel.endswith("settings.json"):
                    d=json.loads(p.read_text(encoding="utf-8"))
                    for k in ["telegram_bot_token","twitch_client_secret","youtube_client_secret","obs_ws_password"]:d.pop(k,None)
                    z.writestr(rel,json.dumps(d,ensure_ascii=False,indent=2))
                continue
            z.write(p,rel)
        model=ROOT/"runtime/live2d/kira"
        if model.exists():
            for p in model.rglob("*"):
                if p.is_file():z.write(p,p.relative_to(ROOT).as_posix())
    out.seek(0);return out
