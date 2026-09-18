from .chat_events import chat_queue

SUPPORTED={"follow","subscribe","gift","raid","cheer"}

def push_stream_event(platform,user,kind,detail=""):
    if kind not in SUPPORTED: return False
    text=f"[{kind}] {detail}".strip()
    return chat_queue.push(platform,user,text,kind)
