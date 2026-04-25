import discord
from discord import app_commands
from discord.ui import Modal, TextInput, Button, View
import aiohttp
from aiohttp import web
import asyncio
from datetime import datetime
import os

TOKEN = os.environ.get('TOKEN')
CHANNEL_ID = 1495457069321556018

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

class ScammerModal(Modal, title='🚨 Report a Scammer'):
    name = TextInput(label="Scammer's name?", placeholder="e.g. MaxMuster#1234")
    discord_user = TextInput(label="Discord username?", placeholder="e.g. @maxmuster", required=False)
    socials = TextInput(label="TikTok / Instagram / WhatsApp / Email?", placeholder="e.g. @maxmuster / +49123456", required=False)
    platform = TextInput(label="Where did you meet them?", placeholder="e.g. Discord, TikTok, Instagram")
    description = TextInput(label="What happened & how much did you lose?", style=discord.TextStyle.paragraph, placeholder="Describe the scam in detail...")

    async def on_submit(self, interaction: discord.Interaction):
        channel = client.get_channel(CHANNEL_ID)
        embed = discord.Embed(
            title="🚨 SCAMMER ALERT 🚨",
            color=0xFF0000,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="⚠️ Reported Scammer", value=f"**{self.name.value}**", inline=False)
        embed.add_field(name="💬 Discord", value=self.discord_user.value or "N/A", inline=True)
        embed.add_field(name="📱 Socials", value=self.socials.value or "N/A", inline=True)
        embed.add_field(name="📍 Found on", value=self.platform.value, inline=True)
        embed.add_field(name="⚠️ Scam Details", value=self.description.value, inline=False)
        embed.add_field(name="❌ Status", value="BANNED & REPORTED - WARN YOUR FRIENDS!", inline=False)
        embed.set_footer(text=f"WE LUV MONEY • Scammer List • Reported by {interaction.user.name}")

        view = VerifyView()
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Report submitted!", ephemeral=True)

class VerifyButton(Button):
    def __init__(self):
        super().__init__(label="✅ Mark as Verified", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.manage_messages:
            embed = interaction.message.embeds[0]
            embed.add_field(name="✅ VERIFIED", value=f"Verified by {interaction.user.name}", inline=False)
            self.disabled = True
            self.label = "✅ Verified"
            await interaction.message.edit(embed=embed, view=self.view)
            await interaction.response.send_message("✅ Marked as verified!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Only moderators can verify!", ephemeral=True)

class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(VerifyButton())

class ReportView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🚨 Report a Scammer", style=discord.ButtonStyle.danger)
    async def report_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(ScammerModal())

async def web_server():
    async def health(request):
        return web.Response(text="Bot is alive!")
    app = web.Application()
    app.router.add_get('/', health)
    app.router.add_get('/health', health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 5000)
    await site.start()

@client.event
async def on_ready():
    await tree.sync()
    await web_server()
    channel = client.get_channel(CHANNEL_ID)
    view = ReportView()
    await channel.send("Click the button below to anonymously report a scammer. Your report will be posted publicly to warn the community.", view=view)
    print(f'Bot is online as {client.user}')

client.run(TOKEN)
