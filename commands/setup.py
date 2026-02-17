import discord
from discord import app_commands
from systems.tickets import TicketDropdown


def setup(bot):
    @bot.tree.command(
        name="setup_tickets",
        description="Setup the ticket system"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_tickets(interaction: discord.Interaction):
        embed = discord.Embed(
            title="Support Ticket System",
            description=(
                "Click below to create a ticket.\n\n"
                "• General support\n"
                "• Report a user\n"
                "• Partnership requests"
            ),
            color=discord.Color.blue(),
        )

        await interaction.channel.send(
            embed=embed,
            view=TicketDropdown()
        )

        await interaction.response.send_message(
            "Ticket system setup complete.",
            ephemeral=True
        )