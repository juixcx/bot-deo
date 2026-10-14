import os
import discord
from discord import app_commands
from discord.ext import commands

from ui import MainView
from bot_helpers import handle_deobf, handle_detect
from engines import ENGINES, SETUP_STATUS

TOKEN = os.environ.get("DISCORD_TOKEN", "")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
    except Exception as e:
        print("sync err:", e)
    try:
        bot.add_view(MainView(bot))  # persistent view
    except Exception as e:
        print("add_view err:", e)
    print(f"[BOT] logged in as {bot.user}")


# ============================================================
# SLASH COMMANDS
# ============================================================
@bot.tree.command(name="panel", description="เปิด panel หลักของบอท")
async def panel_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Luraph Deobfuscator Bot",
        description=(
            "**กดปุ่มด้านล่างเพื่อใช้งาน**\n\n"
            "🔓 **Deobfuscate** — deobf script (auto-detect)\n"
            "🔍 **Detect** — ตรวจ obfuscator\n"
            "⚙️ **Engines** — list engines\n"
            "💚 **Health** — สถานะบอท"
        ),
        color=0xff6b35,
    )
    embed.set_footer(text="discord.gg/kurokoai")
    await interaction.response.send_message(embed=embed, view=MainView(bot))


@bot.tree.command(name="deobf", description="Deobfuscate script")
@app_commands.describe(
    url="URL ของ script",
    code="หรือ paste code",
    engine="force engine (optional)"
)
async def deobf_cmd(interaction: discord.Interaction,
                    url: str = None,
                    code: str = None,
                    engine: str = None):
    await handle_deobf(interaction, url=url, code=code, engine=engine)


@bot.tree.command(name="detect", description="Detect obfuscator")
@app_commands.describe(url="URL ของ script", code="หรือ paste code")
async def detect_cmd(interaction: discord.Interaction,
                     url: str = None, code: str = None):
    await handle_detect(interaction, url=url, code=code)


@bot.tree.command(name="engines", description="List engines")
async def engines_cmd(interaction: discord.Interaction):
    lines = ["**Available Engines:**"]
    for k, v in ENGINES.items():
        st = SETUP_STATUS.get(k, "not loaded")
        emoji = "✅" if st == "complete" else "⏳"
        lines.append(f"{emoji} `{k}` — {v['name']}")
    await interaction.response.send_message("\n".join(lines))


@bot.tree.command(name="health", description="Bot health")
async def health_cmd(interaction: discord.Interaction):
    loaded = sum(1 for s in SETUP_STATUS.values() if s == "complete")
    await interaction.response.send_message(
        f"**Health:**\n"
        f"- Bot: ✅\n"
        f"- Engines: `{loaded}/{len(ENGINES)}`\n"
        f"- Logged in: `{bot.user}`"
    )


if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: DISCORD_TOKEN not set")
        exit(1)
    bot.run(TOKEN)
