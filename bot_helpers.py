import io
import time
import urllib.request
import discord

from engines import ENGINES, SETUP_STATUS, detect, deobfuscate
import cache


def _fetch_script(url: str, code: str = None):
    if code and len(code) > 100:
        return code, None
    if not url:
        return None, "no url/code"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8", errors="replace"), None
    except Exception as e:
        return None, str(e)


async def handle_deobf(interaction: discord.Interaction,
                       url: str = None, code: str = None,
                       engine: str = None):
    await interaction.response.defer(thinking=True)

    script, err = _fetch_script(url, code)
    if err:
        return await interaction.followup.send(f"❌ Fetch failed: {err}")
    if not script or len(script) < 100:
        return await interaction.followup.send("❌ Script too short")

    obf, ver, detected_engine, conf = detect(script)

    if engine and engine in ENGINES:
        chosen = engine
    elif detected_engine:
        chosen = detected_engine
    else:
        return await interaction.followup.send(
            f"❌ Cannot detect obfuscator\n"
            f"Confidence: `{conf}`\n"
            f"Available: `{', '.join(ENGINES.keys())}`\n"
            f"ระบุ engine เองใน modal"
        )

    # cache
    cached = cache.get(script, chosen)
    if cached:
        buf = io.BytesIO(cached.encode("utf-8"))
        buf.seek(0)
        return await interaction.followup.send(
            f"⚡ **Cache hit** — {obf} {ver} → `{chosen}`",
            file=discord.File(buf, filename=f"deobf_{chosen}_cached.lua")
        )

    await interaction.followup.send(
        f"🔍 Detected: `{obf} {ver}` ({conf})\n"
        f"⚙️ Engine: `{chosen}`\n"
        f"⏳ Deobfuscating... (1-15 นาที)"
    )

    output, err = deobfuscate(script, chosen)
    if err:
        return await interaction.followup.send(
            f"❌ Deobf failed\nEngine: `{chosen}`\n```{err[:1800]}```"
        )

    cache.set_(script, chosen, output)

    buf = io.BytesIO(output.encode("utf-8"))
    buf.seek(0)
    await interaction.followup.send(
        f"✅ OK ({len(output):,} bytes)\n"
        f"{obf} {ver} → `{chosen}`",
        file=discord.File(buf, filename=f"deobf_{chosen}_{int(time.time())}.lua")
    )


async def handle_detect(interaction: discord.Interaction,
                        url: str = None, code: str = None):
    await interaction.response.defer(thinking=True)

    script, err = _fetch_script(url, code)
    if err:
        return await interaction.followup.send(f"❌ Fetch failed: {err}")
    if not script:
        return await interaction.followup.send("❌ No script")

    obf, ver, engine, conf = detect(script)

    await interaction.followup.send(
        f"**Detection:**\n"
        f"- Obfuscator: `{obf}`\n"
        f"- Version: `{ver}`\n"
        f"- Suggested engine: `{engine or 'none'}`\n"
        f"- Confidence: `{conf}`\n"
        f"- Size: `{len(script):,} bytes`"
    )
