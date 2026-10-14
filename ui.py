import io
import time
import discord


class MainView(discord.ui.View):
    """ปุ่มหลักของบอท"""

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Deobfuscate", style=discord.ButtonStyle.success,
                       custom_id="deobf_btn", emoji="🔓")
    async def deobf_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DeobfModal())

    @discord.ui.button(label="Detect", style=discord.ButtonStyle.primary,
                       custom_id="detect_btn", emoji="🔍")
    async def detect_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DetectModal())

    @discord.ui.button(label="Engines", style=discord.ButtonStyle.secondary,
                       custom_id="engines_btn", emoji="⚙️")
    async def engines_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        from engines import ENGINES, SETUP_STATUS
        lines = ["**Available Engines:**"]
        for k, v in ENGINES.items():
            st = SETUP_STATUS.get(k, "not loaded")
            emoji = "✅" if st == "complete" else "⏳"
            lines.append(f"{emoji} `{k}` — {v['name']} ({st})")
        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    @discord.ui.button(label="Health", style=discord.ButtonStyle.secondary,
                       custom_id="health_btn", emoji="💚")
    async def health_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        from engines import ENGINES, SETUP_STATUS
        loaded = sum(1 for s in SETUP_STATUS.values() if s == "complete")
        await interaction.response.send_message(
            f"**Health:** ✅ online\n"
            f"Engines: `{loaded}/{len(ENGINES)}`",
            ephemeral=True
        )


class DeobfModal(discord.ui.Modal, title="Deobfuscate Script"):
    url = discord.ui.TextInput(
        label="Script URL (ถ้ามี)",
        placeholder="https://raw.githubusercontent.com/...",
        required=False,
        style=discord.TextStyle.short,
    )
    code = discord.ui.TextInput(
        label="หรือ paste code",
        placeholder="paste obfuscated code here",
        required=False,
        style=discord.TextStyle.paragraph,
    )
    engine = discord.ui.TextInput(
        label="Engine (เว้นว่าง = auto-detect)",
        placeholder="luraph_14.9 / moonsec / prometheus / ...",
        required=False,
        style=discord.TextStyle.short,
    )

    async def on_submit(self, interaction: discord.Interaction):
        from bot_helpers import handle_deobf
        await handle_deobf(
            interaction,
            url=self.url.value.strip() or None,
            code=self.code.value.strip() or None,
            engine=self.engine.value.strip() or None,
        )


class DetectModal(discord.ui.Modal, title="Detect Obfuscator"):
    url = discord.ui.TextInput(
        label="Script URL",
        placeholder="https://raw.githubusercontent.com/...",
        required=False,
    )
    code = discord.ui.TextInput(
        label="หรือ paste code",
        required=False,
        style=discord.TextStyle.paragraph,
    )

    async def on_submit(self, interaction: discord.Interaction):
        from bot_helpers import handle_detect
        await handle_detect(
            interaction,
            url=self.url.value.strip() or None,
            code=self.code.value.strip() or None,
        )
