import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(bot.guilds)} servers"
        )
    )
    print(f"Bot is online as {bot.user}")

async def load_cogs():
    for cog in ["moderation", "protection", "tickets", "giveaways"]:
        await bot.load_extension(cog)
        print(f"Loaded: {cog}")

@bot.event
async def setup_hook():
    await load_cogs()

bot.run(TOKEN)
