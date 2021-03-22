from discord import Message, RawMessageUpdateEvent, RawMessageDeleteEvent, VoiceState, Member, User, Guild
from discord.abc import GuildChannel
from discord.ext import commands

from loguru import logger
from os import getenv

from src.internal.bot import Bot

primary_guild = int(getenv("GUILD"))


class Events(commands.Cog):
    """A cog for collecting events."""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        """
        Receive and store message events from Discord.

        Only messages in guilds are stored.
        """

        if not (message.guild and message.guild.id == primary_guild):
            return

        if message.author.bot:
            return

        data = {
            "content": message.content
        }

        await self.bot.db.create_event(
            type="message_create",
            data=data,
            channel=message.channel.id,
            category=message.channel.category.id if message.channel.category else None,
            user=message.author.id,
            event_id=message.id,
        )

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload: RawMessageUpdateEvent):
        """
        Receive and store message edit events.

        Only messages in guilds are stored.
        """

        channel = self.bot.get_channel(payload.channel_id)
        if not (isinstance(channel, GuildChannel) and channel.guild.id == primary_guild):
            return

        try:
            data = {
                "content": payload.data["content"]
            }
        except:
            return  # Edit is something like an embed expand or supress

        await self.bot.db.create_event(
            type="message_update",
            data=data,
            channel=payload.channel_id,
            category=channel.category.id if channel.category else None,
            user=int(payload.data["author"]["id"]),
            event_id=payload.message_id,
        )

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: RawMessageDeleteEvent):
        """
        Receive and store message delete events.

        Only messages in guilds are stored.
        """

        channel = self.bot.get_channel(payload.channel_id)
        if not (isinstance(channel, GuildChannel) and channel.guild.id == primary_guild):
            return

        await self.bot.db.create_event(
            type="message_delete",
            data={},
            channel=payload.channel_id,
            category=channel.category.id if channel.category else None,
            event_id=payload.message_id,
        )

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        """
        Receive and store voice state updates, classified by whether they're join, leave, or move channel.

        Only voice states in guilds are stored.
        """

        if member.guild.id != primary_guild:
            return

        if before.channel and after.channel:
            event_type = "voice_move"
            channel = after.channel
        elif before.channel and not after.channel:
            event_type = "voice_leave"
            channel = before.channel
        elif after.channel and not before.channel:
            event_type = "voice_join"
            channel = after.channel
        else:
            # State update is not a channel leave/join/switch, ignore
            return

        await self.bot.db.create_event(
            type=event_type,
            data={},
            channel=channel.id,
            category=channel.category.id if channel.category else None,
            user=member.id,
        )

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        """
        Receive and store member join events.
        """

        if member.guild.id != primary_guild:
            return

        await self.bot.db.create_event(
            type="member_join",
            data={},
            user=member.id,
        )

    @commands.Cog.listener()
    async def on_member_leave(self, member: Member):
        """
        Receive and store member leave events.
        """

        if member.guild.id != primary_guild:
            return

        await self.bot.db.create_event(
            type="member_leave",
            data={},
            user=member.id
        )

    @commands.Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
        """
        Receive and store member update events.
        """

        if before.guild.id != primary_guild:
            return

        if before.status != after.status:
            return  # Don't care about status updates
        if before.activity != after.activity:
            return  # Don't care about activity updates
        if before.pending and not after.pending:
            data = {
                "event": "member_gate_accept",
            }
        elif before.nick != after.nick:
            data = {
                "event": "nickname_change",
                "before": before.nick,
                "after": after.nick,
            }
        elif before.roles != after.roles:
            data = {
                "event": "role_change",
                "before": [r.id for r in before.roles],
                "after": [r.id for r in after.roles],
            }
        else:
            return  # This can't? happen (I think)

        await self.bot.db.create_event(
            type="member_update",
            data=data,
            user=after.id,
        )

    @commands.Cog.listener()
    async def on_member_ban(self, guild: Guild, member: User):
        """
        Receive and store member ban events.
        """

        if guild.id != primary_guild:
            return

        await self.bot.db.create_event(
            type="member_ban",
            data={},
            user=member.id,
        )

    @commands.Cog.listener()
    async def on_member_unban(self, guild: Guild, user: User):
        """
        Receive and store member unban events.
        """

        if guild.id != primary_guild:
            return

        await self.bot.db.create_event(
            type="member_unban",
            data={},
            user=user.id,
        )


def setup(bot: Bot):
    bot.add_cog(Events(bot))
