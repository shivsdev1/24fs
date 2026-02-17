import discord
from core.config import config
from core.storage import levels_data, save_json, LEVELS_FILE
from core.xp import get_level_from_xp

def get_user_data(user_id: int):
    uid = str(user_id)
    if uid not in levels_data:
        levels_data[uid] = {"xp": 0, "level": 0, "last_message": 0}
    return levels_data[uid]

async def handle_level_up(member, guild, old_level, new_level):
    rewards = config.get("level_rewards", {})
    role_given = None

    if str(new_level) in rewards:
        role = discord.utils.get(guild.roles, name=rewards[str(new_level)])
        if role:
            if config.get("only_keep_highest_role"):
                for lvl, name in rewards.items():
                    if int(lvl) < new_level:
                        old = discord.utils.get(guild.roles, name=name)
                        if old in member.roles:
                            await member.remove_roles(old)
            await member.add_roles(role)
            role_given = role

    if config.get("level_up_channel"):
        if config["level_up_mode"] == "all" or role_given:
            channel = guild.get_channel(config["level_up_channel"])
            if channel:
                embed = discord.Embed(
                    title="🎉 Level Up!",
                    description=f"{member.mention} reached **Level {new_level}**",
                    color=discord.Color.gold()
                )
                if role_given:
                    embed.add_field(
                        name="Reward",
                        value=role_given.mention,
                        inline=False
                    )
                await channel.send(embed=embed)

    save_json(LEVELS_FILE, levels_data)