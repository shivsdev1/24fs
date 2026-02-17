import discord
from discord import app_commands
from systems.levels import get_user_data
from core.xp import calculate_xp_for_level


def setup(bot):
    @bot.tree.command(
        name="rank",
        description="Check your rank"
    )
    async def rank(
        interaction: discord.Interaction,
        member: discord.Member | None = None
    ):
        target = member or interaction.user
        data = get_user_data(target.id)

        level = data["level"]
        total_xp = data["xp"]

        used_xp = sum(
            calculate_xp_for_level(i)
            for i in range(1, level + 1)
        )
        current = total_xp - used_xp
        needed = calculate_xp_for_level(level + 1)

        embed = discord.Embed(
            title=f"{target.name}'s Rank",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(
            url=target.avatar.url
            if target.avatar else target.default_avatar.url
        )
        embed.add_field(name="Level", value=level)
        embed.add_field(name="Total XP", value=f"{total_xp:,}")
        embed.add_field(
            name="Progress",
            value=f"{current}/{needed} XP",
            inline=False
        )

        await interaction.response.send_message(embed=embed)