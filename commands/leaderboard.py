import discord
from discord import app_commands
from core.storage import levels_data


def setup(bot):
    @bot.tree.command(
        name="leaderboard",
        description="View XP leaderboard"
    )
    async def leaderboard(interaction: discord.Interaction):
        top = sorted(
            levels_data.items(),
            key=lambda x: x[1]["xp"],
            reverse=True
        )[:10]

        embed = discord.Embed(
            title="Server Leaderboard",
            color=discord.Color.gold()
        )

        for i, (uid, data) in enumerate(top, 1):
            user = await bot.fetch_user(int(uid))
            embed.add_field(
                name=f"{i}. {user.name}",
                value=f"Level {data['level']} • {data['xp']:,} XP",
                inline=False
            )

        await interaction.response.send_message(embed=embed)