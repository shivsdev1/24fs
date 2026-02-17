import discord
from datetime import datetime
from core.config import config


async def on_member_join(bot, member: discord.Member):
    if not config.get("welcome_channel"):
        return

    channel = bot.get_channel(config["welcome_channel"])
    if not channel:
        return

    member_count = len(member.guild.members)

    embed = discord.Embed(
        title="Welcome to the Server!",
        description=(
            f"{member.mention} you are our "
            f"**{member_count}th** member!"
        ),
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )

    embed.set_thumbnail(
        url=member.avatar.url
        if member.avatar else member.default_avatar.url
    )

    embed.set_footer(text=f"Member #{member_count}")

    await channel.send(embed=embed)