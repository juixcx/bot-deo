import os
import re
import time
import shutil
import zipfile
import subprocess
import urllib.request

# ============================================================
# ENGINES — git only
# ============================================================
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
    "prometheus_v2": {
        "name": "Prometheus v2 (0x251)",
        "type": "git",
        "repo": "https://github.com/0x251/Prometheus-DeobfuscatorV2.git",
        "clone_dir": "/tmp/engines/prometheus_v2",
        "cli_dir": ".",
        "cli_file": None,  # autodetect
        "cli_args": [],
    },
    "prometheus": {
        "name": "Prometheus (official)",
        "type": "git",
        "repo": "https://github.com/levno-710/Prometheus.git",
        "clone_dir": "/tmp/engines/prometheus",
        "cli_dir": ".",
        "cli_file": None,
        "cli_args": [],
    },
    "unveilr": {
        "name": "Unveilr (IronBrew 2)",
        "type": "git",
        "repo": "https://github.com/Unveilr/unveilr.git",
        "clone_dir": "/tmp/engines/unveilr",
        "cli_dir": ".",
        "cli_file": None,
        "cli_args": [],
    },
    "moonsec_v3": {
        "name": "MoonSec V3",
        "type": "git",
        "repo": "https://github.com/PandaGamingTV/MoonSecV3-Deobfuscator.git",
        "clone_dir": "/tmp/engines/moonsec_v3",
        "cli_dir": ".",
        "cli_file": None,
        "cli_args": [],
    },
    "luaobfuscator": {
        "name": "LuaObfuscator",
        "type": "git",
        "repo": "https://github.com/LuaObfuscator/LuaObfuscator.git",
        "clone_dir": "/tmp/engines/luaobfuscator",
        "cli_dir": ".",
        "cli_file": None,
        "cli_args": [],
    },
    "luadec": {
        "name": "Luadec (bytecode)",
        "type": "git",
        "repo": "https://github.com/lua-tools/luadec.git",
        "clone_dir": "/tmp/engines/luadec",
        "cli_dir": ".",
        "cli_file": None,
        "cli_args": [],
        "make": True,
    },
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

    # bin download ถ้ามี
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
                    try: os.chmod(fp, 0o755)
                    except: pass

    # make ถ้าจำเป็น (luadec)
    if cfg.get("make"):
        try:
            subprocess.run(["make", "-j4"], cwd=cd, timeout=300, capture_output=True)
        except Exception:
            pass


def setup_engine(key):
    if SETUP_STATUS.get(key) == "complete":
        return True, "ok"
    cfg = ENGINES[key]
    try:
        _setup_git(cfg)
        SETUP_STATUS[key] = "complete"
        return True, "ok"
    except Exception as e:
        SETUP_STATUS[key] = f"failed: {e}"
        return False, SETUP_STATUS[key]


def _find_cli(d):
    for c in ["main.py", "cli.py", "deobf.py", "deobfuscate.py",
              "unveilr.py", "prometheus.py", "run.py",
              "__main__.py", "index.js", "app.js"]:
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

    # Prometheus — v2 ก่อน
    if re.search(r"prometheus[\s\-_]?v?2", head, re.I):
        return ("Prometheus", "2", "prometheus_v2", "high")
    if re.search(r"prometheus", head, re.I):
        return ("Prometheus", "unknown", "prometheus", "high")

    if re.search(r"moonsec.{0,10}v?3", head, re.I):
        return ("MoonSec", "3", "moonsec_v3", "high")
    if re.search(r"moonsec", head, re.I):
        return ("MoonSec", "unknown", "moonsec_v3", "medium")

    if re.search(r"moonveil", head, re.I):
        return ("Moonveil", "unknown", None, "high")

    if re.search(r"ironbrew|ib2", head, re.I):
        return ("IronBrew", "2", "unveilr", "high")

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

    cli_dir = os.path.join(cfg["clone_dir"], cfg["cli_dir"])
    cli_file = cfg.get("cli_file")

    if not cli_file:
        cli_dir, cli_file = _find_cli(cfg["clone_dir"])
        if not cli_dir:
            return None, f"CLI file not found in {cfg['clone_dir']}\ncontents: {os.listdir(cfg['clone_dir'])[:30]}"

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
