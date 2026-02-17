import discord
from discord import app_commands
from systems.levels import get_user_data
from core.storage import save_json, LEVELS_FILE
from core.xp import calculate_xp_for_level
from core.config import config


def setup(bot):
    @bot.tree.command(
        name="setlevel",
        description="Set a user's level"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setlevel(
        interaction: discord.Interaction,
        member: discord.Member,
        level: int
    ):
        data = get_user_data(member.id)

        data["xp"] = sum(
            calculate_xp_for_level(i)
            for i in range(1, level + 1)
        )
        data["level"] = level

        save_json(LEVELS_FILE, data)

        await interaction.response.send_message(
            f"Set {member.mention} to level {level}.",
            ephemeral=True
        )

    @bot.tree.command(
        name="config",
        description="View bot config"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def show_config(interaction: discord.Interaction):
        embed = discord.Embed(
            title="Bot Configuration",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="XP Range",
            value=f"{config['xp_per_message_min']}–{config['xp_per_message_max']}"
        )
        embed.add_field(
            name="Cooldown",
            value=f"{config['xp_cooldown_ms']} ms"
        )
        embed.add_field(
            name="Level Mode",
            value=config["level_up_mode"]
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )