import discord
from discord import app_commands
from discord.ui import Modal, TextInput, Button, View
import aiohttp
from aiohttp import web
import asyncio
from datetime import datetime
import os

TOKEN = os.environ.get('TOKEN')
SCAMMER_CHANNEL_ID = 1495457069321556018
REVIEW_CHANNEL_ID = 1495457066809168094
INTRO_CHANNEL_ID = 1495457040049635570

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ─────────────────────────────────────────
# SCAMMER SYSTEM
# ─────────────────────────────────────────

class ScammerModal(Modal, title='🚨 Report a Scammer'):
    name = TextInput(label="Scammer's name?", placeholder="e.g. MaxMuster#1234")
    discord_user = TextInput(label="Discord username?", placeholder="e.g. @maxmuster", required=False)
    socials = TextInput(label="TikTok / Instagram / WhatsApp / Email?", placeholder="e.g. @maxmuster / +49123456", required=False)
    platform = TextInput(label="Where did you meet them?", placeholder="e.g. Discord, TikTok, Instagram")
    description = TextInput(label="What happened & how much did you lose?", style=discord.TextStyle.paragraph, placeholder="Describe the scam in detail...")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        channel = client.get_channel(SCAMMER_CHANNEL_ID)
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
        await interaction.followup.send("✅ Report submitted!", ephemeral=True)

class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ Mark as Verified", style=discord.ButtonStyle.success, custom_id="verify_scammer")
    async def verify_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.guild_permissions.manage_messages:
            embed = interaction.message.embeds[0]
            embed.add_field(name="✅ VERIFIED", value=f"Verified by {interaction.user.name}", inline=False)
            button.disabled = True
            button.label = "✅ Verified"
            await interaction.message.edit(embed=embed, view=self)
            await interaction.response.send_message("✅ Marked as verified!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Only moderators can verify!", ephemeral=True)

class ReportView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🚨 Report a Scammer", style=discord.ButtonStyle.danger, custom_id="report_scammer")
    async def report_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(ScammerModal())

# ─────────────────────────────────────────
# SELLER REVIEW SYSTEM
# ─────────────────────────────────────────

class ReviewModal(Modal, title='⭐ Leave a Seller Review'):
    seller = TextInput(label="Seller's Discord username?", placeholder="e.g. @maxmuster")
    stars = TextInput(label="How many stars? (1-5)", placeholder="e.g. 5")
    item = TextInput(label="What did you buy?", placeholder="e.g. Instagram followers")
    experience = TextInput(label="How was your experience?", style=discord.TextStyle.paragraph, placeholder="Describe your experience in detail...")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        channel = client.get_channel(REVIEW_CHANNEL_ID)

        try:
            star_count = int(self.stars.value)
            star_count = max(1, min(5, star_count))
        except:
            star_count = 5

        stars_display = "⭐" * star_count + "🌑" * (5 - star_count)

        embed = discord.Embed(
            title="⭐ Seller Review",
            color=0xFFD700,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="💼 Seller", value=f"**{self.seller.value}**", inline=True)
        embed.add_field(name="⭐ Rating", value=f"{stars_display} ({star_count}/5)", inline=True)
        embed.add_field(name="🛒 Item Bought", value=self.item.value, inline=False)
        embed.add_field(name="💬 Experience", value=self.experience.value, inline=False)
        embed.set_footer(text=f"WE LUV MONEY • Seller Reviews • Review by {interaction.user.name}")
        await channel.send(embed=embed)
        await interaction.followup.send("✅ Review submitted! Thank you!", ephemeral=True)

class ReviewView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="⭐ Leave a Review", style=discord.ButtonStyle.primary, custom_id="leave_review")
    async def review_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(ReviewModal())

# ─────────────────────────────────────────
# INTRODUCTION SYSTEM
# ─────────────────────────────────────────

class IntroModal(Modal, title='👋 Introduce Yourself'):
    name = TextInput(label="What is your name?", placeholder="e.g. Max")
    sells = TextInput(label="What do you sell?", placeholder="e.g. Digital products, Instagram followers")
    location = TextInput(label="Where are you from?", placeholder="e.g. Berlin, Germany")
    socials = TextInput(label="Your Social Media?", placeholder="e.g. TikTok: @max, Instagram: @max", required=False)
    goal = TextInput(label="What is your goal here?", style=discord.TextStyle.paragraph, placeholder="e.g. I want to grow my business and connect with buyers...")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        channel = client.get_channel(INTRO_CHANNEL_ID)

        embed = discord.Embed(
            title="👋 New Member Introduction",
            description=f"Meet {interaction.user.mention}! They have just joined **WE LUV MONEY** and are ready to do business! 💰",
            color=0xFFD700,
            timestamp=datetime.utcnow()
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="👤 Name", value=self.name.value, inline=True)
        embed.add_field(name="🌍 Location", value=self.location.value, inline=True)
        embed.add_field(name="💼 Sells", value=self.sells.value, inline=False)
        embed.add_field(name="📱 Social Media", value=self.socials.value or "N/A", inline=False)
        embed.add_field(name="🎯 Goal", value=self.goal.value, inline=False)
        embed.set_footer(
            text="WE LUV MONEY • Welcome to the Family 💰",
            icon_url="https://cdn.discordapp.com/icons/1495454024919552090/a785cbb70d8d0f9c8688fe108f2e7181.webp?size=2048"
        )
        await channel.send(embed=embed)
        await interaction.followup.send("✅ Introduction posted! Welcome to WE LUV MONEY! 💰", ephemeral=True)

class IntroView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="👋 Introduce Yourself", style=discord.ButtonStyle.success, custom_id="introduce_yourself")
    async def intro_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(IntroModal())

# ─────────────────────────────────────────
# SETUP COMMANDS
# ─────────────────────────────────────────

@tree.command(name="setup-scammer", description="Post the Report a Scammer button (Admin only)")
async def setup_scammer(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        channel = client.get_channel(SCAMMER_CHANNEL_ID)
        embed = discord.Embed(
            title="🚨 Report a Scammer",
            description="Have you been scammed by someone in this server or on social media?\n\nClick the button below to report them and protect the community!",
            color=0xFF0000
        )
        embed.set_footer(text="WE LUV MONEY • Scammer List")
        view = ReportView()
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Scammer report button posted!", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Only admins can use this command!", ephemeral=True)

@tree.command(name="setup-reviews", description="Post the Leave a Review button (Admin only)")
async def setup_reviews(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        channel = client.get_channel(REVIEW_CHANNEL_ID)
        embed = discord.Embed(
            title="⭐ Leave a Seller Review",
            description="Bought something from a seller here?\n\nShare your experience and help the community know who to trust!",
            color=0xFFD700
        )
        embed.set_footer(text="WE LUV MONEY • Seller Reviews")
        view = ReviewView()
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Review button posted!", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Only admins can use this command!", ephemeral=True)

@tree.command(name="setup-introductions", description="Post the Introduce Yourself button (Admin only)")
async def setup_introductions(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        channel = client.get_channel(INTRO_CHANNEL_ID)
        embed = discord.Embed(
            title="👋 INTRODUCE YOURSELF",
            description="Welcome to **WE LUV MONEY**! 💰\n\nWe're glad to have you here. Please introduce yourself to the community by clicking the button below!",
            color=0xFFD700
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/icons/1495454024919552090/a785cbb70d8d0f9c8688fe108f2e7181.webp?size=2048")
        embed.set_author(
            name="WE LUV MONEY",
            icon_url="https://cdn.discordapp.com/icons/1495454024919552090/a785cbb70d8d0f9c8688fe108f2e7181.webp?size=2048"
        )
        embed.set_footer(text="WE LUV MONEY • Welcome to the Family 💰")
        view = IntroView()
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Introduction button posted!", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Only admins can use this command!", ephemeral=True)

# ─────────────────────────────────────────
# WEB SERVER & BOT START
# ─────────────────────────────────────────

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
    client.add_view(ReportView())
    client.add_view(VerifyView())
    client.add_view(ReviewView())
    client.add_view(IntroView())
    await tree.sync()
    await web_server()
    print(f'✅ Bot is online as {client.user}')

client.run(TOKEN)
