import discord
import asyncio
from datetime import datetime
from core.config import config, save_config
from core.storage import tickets_data, save_json, TICKETS_FILE


class TicketPurposeSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="General Support",
                description="General help and questions",
                emoji="🎫"
            ),
            discord.SelectOption(
                label="Partnership Request",
                description="Request a partnership",
                emoji="🤝"
            ),
            discord.SelectOption(
                label="Report a User",
                description="Report rule violations",
                emoji="🚨"
            ),
        ]
        super().__init__(
            placeholder="Select ticket purpose...",
            options=options,
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: discord.Interaction):
        await create_ticket(interaction, self.values[0])


class TicketDropdown(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketPurposeSelect())


class TicketControls(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Close Ticket",
        style=discord.ButtonStyle.danger,
        emoji="🔒"
    )
    async def close_ticket(self, interaction, _):
        await interaction.response.send_modal(
            TicketFeedbackModal(interaction.channel)
        )

    @discord.ui.button(
        label="Add User",
        style=discord.ButtonStyle.primary,
        emoji="➕"
    )
    async def add_user(self, interaction, _):
        await interaction.response.send_modal(
            AddUserModal(interaction.channel)
        )

    @discord.ui.button(
        label="Transcript",
        style=discord.ButtonStyle.secondary,
        emoji="📝"
    )
    async def transcript(self, interaction, _):
        await generate_transcript(interaction)


async def create_ticket(interaction: discord.Interaction, purpose: str):
    guild = interaction.guild
    member = interaction.user

    ticket_number = len(
        [c for c in guild.channels if c.name.startswith("ticket-")]
    ) + 1

    category = None
    if config.get("ticket_category"):
        category = guild.get_channel(config["ticket_category"])

    if not category:
        category = await guild.create_category("Tickets")
        config["ticket_category"] = category.id
        save_config(config)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }

    channel = await guild.create_text_channel(
        name=f"ticket-{ticket_number}",
        category=category,
        overwrites=overwrites,
    )

    tickets_data[str(channel.id)] = {
        "user_id": member.id,
        "purpose": purpose,
        "created_at": datetime.utcnow().isoformat(),
        "status": "open",
    }
    save_json(TICKETS_FILE, tickets_data)

    embed = discord.Embed(
        title=f"Support Ticket #{ticket_number}",
        description=(
            f"**Purpose:** {purpose}\n\n"
            "Thank you for creating a ticket. "
            "Our support team will assist you shortly."
        ),
        color=discord.Color.blue(),
        timestamp=datetime.utcnow(),
    )
    embed.set_footer(text=f"Ticket created by {member.name}")

    await channel.send(
        member.mention,
        embed=embed,
        view=TicketControls()
    )

    await interaction.response.send_message(
        f"Ticket created: {channel.mention}",
        ephemeral=True
    )


class TicketFeedbackModal(discord.ui.Modal, title="Ticket Feedback"):
    feedback = discord.ui.TextInput(
        label="How was your support experience?",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=True,
    )

    def __init__(self, channel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        ticket = tickets_data.get(str(self.channel.id))

        if ticket:
            ticket["feedback"] = self.feedback.value
            ticket["status"] = "closed"
            ticket["closed_at"] = datetime.utcnow().isoformat()
            save_json(TICKETS_FILE, tickets_data)

        await interaction.response.send_message(
            "Thanks for the feedback. Closing ticket in 5 seconds.",
            ephemeral=True
        )

        if config.get("ticket_log_channel"):
            await send_ticket_log(self.channel, self.feedback.value)

        await asyncio.sleep(5)
        await self.channel.delete()


class AddUserModal(discord.ui.Modal, title="Add User to Ticket"):
    user_id = discord.ui.TextInput(
        label="User ID or Mention",
        required=True
    )

    def __init__(self, channel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        try:
            uid = int(self.user_id.value.strip("<@!>"))
            user = await interaction.guild.fetch_member(uid)

            await self.channel.set_permissions(
                user,
                read_messages=True,
                send_messages=True
            )

            await interaction.response.send_message(
                f"Added {user.mention} to the ticket.",
                ephemeral=True
            )
        except Exception:
            await interaction.response.send_message(
                "Invalid user.",
                ephemeral=True
            )


async def generate_transcript(interaction: discord.Interaction):
    channel = interaction.channel
    await interaction.response.defer(ephemeral=True)

    messages = []
    async for msg in channel.history(limit=None, oldest_first=True):
        messages.append(msg)

    content = [
        f"Transcript for {channel.name}",
        f"Generated at {datetime.utcnow()}",
        "=" * 50,
        "",
    ]

    for msg in messages:
        time = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        content.append(f"[{time}] {msg.author.name}: {msg.content}")

        for a in msg.attachments:
            content.append(f"  [Attachment] {a.url}")

        content.append("")

    path = f"bot_data/transcript_{channel.id}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(content))

    await interaction.followup.send(
        file=discord.File(path),
        ephemeral=True
    )


async def send_ticket_log(channel, feedback):
    log_channel = channel.guild.get_channel(
        config.get("ticket_log_channel")
    )
    if not log_channel:
        return

    ticket = tickets_data.get(str(channel.id))
    user = await channel.guild.fetch_member(ticket["user_id"])

    embed = discord.Embed(
        title=f"Ticket Closed: {channel.name}",
        color=discord.Color.red(),
        timestamp=datetime.utcnow(),
    )
    embed.add_field(
        name="User",
        value=user.mention if user else "Unknown",
        inline=True
    )
    embed.add_field(
        name="Purpose",
        value=ticket.get("purpose", "Unknown"),
        inline=True
    )
    embed.add_field(
        name="Feedback",
        value=feedback[:1024],
        inline=False
    )

    await log_channel.send(embed=embed)