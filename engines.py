import os
import re
import time
import shutil
import zipfile
import subprocess
import urllib.request

BASE_URL = "https://raw.githubusercontent.com/juixcx/jui-99/bf3fd42d3988f5db2a4ec8249227c81313137592"

ENGINES = {
    "luraph_14.9": {
        "name": "Luraph v14.9",
        "type": "git",
        "repo": "https://github.com/KryptIT/luraph-v15-v14.x-deobfuscator.git",
        "clone_dir": "/tmp/engines/luraph_14.9",
        "cli_dir": "Deobfuscator/deobf",
        "cli_file": "cli.py",
        "cli_args": ["--engine", "14.9", "--strings",
                     "--max-runs", "500", "--devirt-rounds", "50",
                     "--timeout", "300", "--budget", "10000000",
                     "--trace-fallback", "--no-hooks", "--debug"],
        "bin_url": "https://github.com/luau-lang/luau/releases/download/0.653/luau-ubuntu.zip",
        "bin_dir": "bin",
        "bin_name": "luau-ast",
    },
    "clyde": {"name": "Clyde", "type": "zip",
              "zip_url": f"{BASE_URL}/ClydeDeobfuscator-main.zip",
              "extract_dir": "/tmp/engines/clyde", "cli_args": []},
    "77fuscator": {"name": "77fuscator", "type": "zip",
                   "zip_url": f"{BASE_URL}/77fuscatorDeobfuscator-main.zip",
                   "extract_dir": "/tmp/engines/77fuscator", "cli_args": []},
    "ironveil": {"name": "Ironveil V1", "type": "zip",
                 "zip_url": f"{BASE_URL}/Ironveil-Deobfuscator-V1-main.zip",
                 "extract_dir": "/tmp/engines/ironveil", "cli_args": []},
    "luaobfuscator": {"name": "LuaObfuscator", "type": "zip",
                      "zip_url": f"{BASE_URL}/LuaObfuscator-Deobfuscator-main.zip",
                      "extract_dir": "/tmp/engines/luaobfuscator", "cli_args": []},
    "moonsec": {"name": "MoonSec", "type": "zip",
                "zip_url": f"{BASE_URL}/MoonsecDeobfuscator-master.zip",
                "extract_dir": "/tmp/engines/moonsec", "cli_args": []},
    "prometheus": {"name": "Prometheus", "type": "zip",
                   "zip_url": f"{BASE_URL}/Prometheus-Deobfuscator-main.zip",
                   "extract_dir": "/tmp/engines/prometheus", "cli_args": []},
    "moonveil": {"name": "Moonveil", "type": "zip",
                 "zip_url": f"{BASE_URL}/moonveilvro-main.zip",
                 "extract_dir": "/tmp/engines/moonveil", "cli_args": []},
    "ib2": {"name": "IronBrew 2", "type": "zip",
            "zip_url": f"{BASE_URL}/ib2-deobf.zip",
            "extract_dir": "/tmp/engines/ib2", "cli_args": []},
    "hercules": {"name": "Hercules", "type": "zip",
                 "zip_url": f"{BASE_URL}/hercules-deobfuscator-main.zip",
                 "extract_dir": "/tmp/engines/hercules", "cli_args": []},
}

SETUP_STATUS = {}


# ============================================================
# SETUP
# ============================================================
def _setup_git(cfg):
    cd = cfg["clone_dir"]
    if not os.path.exists(cd):
        subprocess.run(["git", "clone", "--depth=1", cfg["repo"], cd],
                       check=True, capture_output=True, timeout=300)
    if cfg.get("bin_url"):
        bd = os.path.join(cd, cfg["cli_dir"], cfg["bin_dir"])
        os.makedirs(bd, exist_ok=True)
        bp = os.path.join(bd, cfg["bin_name"])
        if not os.path.exists(bp):
            z = os.path.join(bd, "bin.zip")
            urllib.request.urlretrieve(cfg["bin_url"], z)
            with zipfile.ZipFile(z) as zf:
                zf.extractall(bd)
            os.remove(z)
            for f in os.listdir(bd):
                fp = os.path.join(bd, f)
                if os.path.isfile(fp):
                    try:
                        os.chmod(fp, 0o755)
                    except Exception:
                        pass


def _setup_zip(cfg):
    ed = cfg["extract_dir"]
    if os.path.exists(ed) and os.listdir(ed):
        return
    os.makedirs(ed, exist_ok=True)
    zp = f"/tmp/{os.path.basename(cfg['zip_url'])}"
    if not os.path.exists(zp):
        urllib.request.urlretrieve(cfg["zip_url"], zp)
    with zipfile.ZipFile(zp) as z:
        z.extractall(ed)
    items = os.listdir(ed)
    if len(items) == 1 and os.path.isdir(os.path.join(ed, items[0])):
        inner = os.path.join(ed, items[0])
        for f in os.listdir(inner):
            shutil.move(os.path.join(inner, f), os.path.join(ed, f))
        os.rmdir(inner)


def setup_engine(key):
    if SETUP_STATUS.get(key) == "complete":
        return True, "ok"
    cfg = ENGINES[key]
    try:
        if cfg["type"] == "git":
            _setup_git(cfg)
        else:
            _setup_zip(cfg)
        SETUP_STATUS[key] = "complete"
        return True, "ok"
    except Exception as e:
        SETUP_STATUS[key] = f"failed: {e}"
        return False, SETUP_STATUS[key]


def _find_cli(d):
    for c in ["main.py", "cli.py", "deobf.py", "deobfuscate.py",
              "index.js", "app.js", "run.py", "__main__.py"]:
        for root, _, files in os.walk(d):
            if c in files:
                return root, c
    return None, None


# ============================================================
# DETECT
# ============================================================
def detect(script: str):
    head = script[:5000]
    if "wearedevs.net/obfuscator" in head:
        return ("WeAreDevs", "1.0.0", None, "high")
    m = re.search(r"Luraph Obfuscator v?([\d.]+)", head, re.I)
    if m:
        return ("Luraph", m.group(1), "luraph_14.9", "high")
    if re.search(r"lura\.ph|luraph", head, re.I):
        return ("Luraph", "unknown", "luraph_14.9", "medium")
    if re.search(r"prometheus", head, re.I):
        return ("Prometheus", "unknown", "prometheus", "high")
    if re.search(r"moonveil", head, re.I):
        return ("Moonveil", "unknown", "moonveil", "high")
    if re.search(r"moonsec", head, re.I):
        return ("MoonSec", "unknown", "moonsec", "high")
    if re.search(r"ironbrew|ib2", head, re.I):
        return ("IronBrew", "2", "ib2", "high")
    if re.search(r"hercules", head, re.I):
        return ("Hercules", "unknown", "hercules", "high")
    if re.search(r"77fuscator", head, re.I):
        return ("77fuscator", "unknown", "77fuscator", "high")
    if re.search(r"ironveil", head, re.I):
        return ("Ironveil", "V1", "ironveil", "high")
    if re.search(r"clyde", head, re.I):
        return ("Clyde", "unknown", "clyde", "medium")
    if re.search(r"luaobfuscator", head, re.I):
        return ("LuaObfuscator", "unknown", "luaobfuscator", "high")
    return ("Unknown", "unknown", None, "none")


# ============================================================
# DEOBF
# ============================================================
def deobfuscate(script: str, engine_key: str):
    ok, msg = setup_engine(engine_key)
    if not ok:
        return None, f"setup failed: {msg}"

    cfg = ENGINES[engine_key]
    workdir = f"/tmp/botdeobf_{int(time.time())}"
    os.makedirs(workdir, exist_ok=True)
    in_path = os.path.join(workdir, "input.lua")
    out_path = os.path.join(workdir, "output.lua")

    with open(in_path, "w", encoding="utf-8") as f:
        f.write(script)

    if cfg["type"] == "git":
        cli_dir = os.path.join(cfg["clone_dir"], cfg["cli_dir"])
        cli_file = cfg["cli_file"]
    else:
        cli_dir, cli_file = _find_cli(cfg["extract_dir"])
        if not cli_dir:
            return None, f"CLI not found in {cfg['extract_dir']}"

    args = ["python", cli_file, in_path, "-o", out_path] + cfg.get("cli_args", [])
    try:
        proc = subprocess.run(args, cwd=cli_dir, capture_output=True,
                              text=True, timeout=900)
    except subprocess.TimeoutExpired:
        return None, "timeout 900s"
    except Exception as e:
        return None, str(e)

    if not os.path.exists(out_path):
        err = (proc.stderr or proc.stdout or "no output")[-1500:]
        return None, err

    with open(out_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read(), None
