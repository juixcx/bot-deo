import os
import json
import time
import hashlib

CACHE_DIR = "/tmp/deobf_cache"
CACHE_TTL = 3600 * 24  # 24 ชั่วโมง


def _ensure():
    os.makedirs(CACHE_DIR, exist_ok=True)


def hash_script(script: str, engine: str) -> str:
    h = hashlib.sha256()
    h.update(script.encode("utf-8", errors="replace"))
    h.update(engine.encode("utf-8"))
    return h.hexdigest()


def get(script: str, engine: str):
    _ensure()
    key = hash_script(script, engine)
    path = os.path.join(CACHE_DIR, f"{key}.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as f:
            data = json.load(f)
        if time.time() - data.get("ts", 0) > CACHE_TTL:
            os.remove(path)
            return None
        return data.get("output")
    except Exception:
        return None


def set_(script: str, engine: str, output: str):
    _ensure()
    key = hash_script(script, engine)
    path = os.path.join(CACHE_DIR, f"{key}.json")
    try:
        with open(path, "w") as f:
            json.dump({"ts": time.time(), "output": output, "engine": engine}, f)
    except Exception:
        pass
