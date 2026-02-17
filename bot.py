import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from commands.loader import load_commands
from events.messages import on_message
from events.ready import handle_ready
from events.members import on_member_join

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    load_commands(bot)
    await handle_ready(bot)

@bot.event
async def on_member_join(member):
    await on_member_join(bot, member)

@bot.event
async def on_message(message):
    await on_message(bot, message)
    await bot.process_commands(message)

token = os.getenv("DISCORD_TOKEN")
bot.run(token)