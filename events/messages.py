import random
from datetime import datetime
from discord.ext import commands
from core.config import config
from systems.levels import get_user_data, handle_level_up
from core.xp import get_level_from_xp
from core.storage import save_json, LEVELS_FILE

async def on_message(bot, message):
    if message.author.bot:
        return

    if message.channel.id in config["blacklisted_channels"]:
        return

    if any(r.id in config["blacklisted_roles"] for r in message.author.roles):
        return

    user = get_user_data(message.author.id)
    now = datetime.now().timestamp() * 1000

    if now - user["last_message"] < config["xp_cooldown_ms"]:
        return

    base = random.randint(
        config["xp_per_message_min"],
        config["xp_per_message_max"]
    )

    multiplier = 1
    for name, mult in config["xp_multiplier_channels"].items():
        if name in message.channel.name.lower():
            multiplier = mult
            break

    for role in message.author.roles:
        if role.name in config["xp_multiplier_roles"]:
            multiplier *= config["xp_multiplier_roles"][role.name]

    gained = int(base * multiplier)
    old_level = user["level"]

    user["xp"] += gained
    user["last_message"] = now
    user["level"] = get_level_from_xp(user["xp"])

    save_json(LEVELS_FILE, user)

    if user["level"] > old_level:
        await handle_level_up(message.author, message.guild, old_level, user["level"])