from datetime import datetime

import discord
from discord import Message
from discord.ext import commands
from discord.commands import slash_command

from db.package.crud.thread_list_manage_target import ThreadListManageTargetCrud
from db.package.crud.guild_config import GuildConfigCrud
from db.package.session import get_db


class ThreadListManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_threshold = 10

    def get_bulied_limit(self, guild_id: int) -> int:
        with get_db() as db:
            config = GuildConfigCrud.find_or_create(db, guild_id)

        if config is None or config.thread_list_threshold is None:
            return self.default_threshold

        return config.thread_list_threshold

    @staticmethod
    def is_target(channel: discord.TextChannel) -> bool:
        """スレッドリストを管理するチャンネルかどうかを判定する

        Args:
            channel (discord.TextChannel): 判定するチャンネル

        Returns:
            bool: スレッドリストを管理するチャンネルの場合はTrue、そうでない場合はFalse
        """
        with get_db() as db:
            return ThreadListManageTargetCrud.find(db, channel.guild.id, channel.id) is not None

    @staticmethod
    def build_thread_list_str(channel: discord.TextChannel, item_list_str: str | None) -> str:
        return "\n".join([
            f"**【{channel.mention} に作成されているスレッドの一覧】**",
            "",
            f"{item_list_str if item_list_str is not None else '現在スレッドはありません'}"
        ])

    @staticmethod
    def build_item_list_str(item_strs: list[str]):
        return "\n\n".join(item_strs)

    @staticmethod
    def build_item_str(thread: discord.Thread) -> str:
        created_at = thread.created_at

        if created_at is not None:
            created_at_str = f"<t:{int(created_at.timestamp())}:d> (<t:{int(created_at.timestamp())}:R>)"
        else:
            created_at_timestamp = 1641686400
            created_at_str = f"<t:{created_at_timestamp}:d> よりも前"

        return "\n".join([
            f"**{thread.mention}**",
            f"> 作成者： {thread.owner.mention}",
            f"> 作成日時： {created_at_str}",
        ])

    @staticmethod
    def build_alert_message() -> discord.Embed:
        return discord.Embed(
            title="議論を行う際はスレッドを作成してください",
            description="個別の議論を行う際は、スレッドを作成することを推奨します",
            color=discord.Colour.yellow()
        )

    async def get_last_message(self, channel: discord.TextChannel) -> Message | None:
        """Botが最後に送信したメッセージを取得する

        Args:
            channel (discord.TextChannel): メッセージを取得するチャンネル

        Returns:
            Message | None: メッセージが見つかった場合はメッセージ、見つからなかった場合はNone
        """
        count = 0
        async for message in channel.history(limit=None):
            if message.author == self.bot.user and "作成されているスレッドの一覧" in message.content:
                return message
            else:
                count += 1
                if self.get_bulied_limit(channel.guild.id) < count:
                    return None
        return None

    async def update_thread_list(self, channel: discord.TextChannel, alert: bool = True):
        """スレッドリストを更新する

        Args:
            channel (discord.TextChannel): 更新するチャンネル
            alert (bool, optional): リストメッセージを再生成するときに警告を行うか
        """

        # チャンネル内のスレッドを取得
        threads = channel.threads

        if len(threads) > 0:
            # スレッドがある場合
            item_strs = [self.build_item_str(thread) for thread in threads]
            item_list_str = self.build_item_list_str(item_strs)
        else:
            # スレッドがない場合
            item_list_str = None

        thread_list_str = self.build_thread_list_str(channel, item_list_str)

        # メッセージを取得
        last_message = await self.get_last_message(channel)

        if last_message is None:
            if alert:
                # メッセージがない場合で、警告を行う場合
                await channel.send(thread_list_str, embed=self.build_alert_message())
            else:
                # メッセージがない場合
                await channel.send(thread_list_str)

        else:
            # メッセージがある場合
            await last_message.edit(content=thread_list_str)

    @commands.Cog.listener(name="on_thread_create")
    async def on_thread_create(self, thread: discord.Thread):
        if self.is_target(thread.parent):
            await self.update_thread_list(thread.parent)

    @commands.Cog.listener(name="on_raw_thread_delete")
    async def on_raw_thread_delete(self, payload: discord.RawThreadDeleteEvent):
        channel = self.bot.get_channel(payload.parent_id)
        if self.is_target(channel):
            await self.update_thread_list(channel)

    @commands.Cog.listener(name="on_raw_thread_update")
    async def on_raw_thread_update(self, payload: discord.RawThreadUpdateEvent):
        channel = self.bot.get_channel(payload.parent_id)
        if self.is_target(channel):
            await self.update_thread_list(channel)

    @commands.Cog.listener(name="on_message")
    async def on_message(self, message: Message):
        channel = message.channel

        if type(channel) == discord.Thread:
            channel = channel.parent
        elif type(channel) != discord.TextChannel:
            return

        if self.is_target(channel):
            await self.update_thread_list(channel)

    @slash_command(name="register",
                   description="スレッドリストを管理するチャンネルを登録します")
    async def register_command(self, ctx):
        print(type(ctx))
        # チャンネルを取得
        channel = ctx.channel

        # チャンネルを登録
        with get_db() as db:
            ThreadListManageTargetCrud.find_or_create(db, channel.guild.id, channel.id)

        # メッセージを送信
        await ctx.respond(f"{channel.mention} を登録しました", ephemeral=True)

        # チャンネルのスレッドリストを更新
        await self.update_thread_list(channel, alert=False)

    @slash_command(name="unregister",
                   description="スレッドリストを管理するチャンネルの登録を解除します")
    async def unregister_command(self, ctx):
        # チャンネルを取得
        channel = ctx.channel

        # チャンネルを登録
        with get_db() as db:
            ThreadListManageTargetCrud.destroy(db, channel.guild.id, channel.id)

        # メッセージを送信
        await ctx.respond(f"{channel.mention} を登録解除しました", ephemeral=True)

    @slash_command(name="update",
                   description="スレッドリストを更新します")
    async def update_command(self, ctx):
        # チャンネルを取得
        channel = ctx.channel

        # メッセージを送信
        await ctx.respond(f"{channel.mention} のスレッドリストを更新します", ephemeral=True)

        # チャンネルのスレッドリストを更新
        await self.update_thread_list(channel)

    @slash_command(name="set_threshold",
                   description="許容するスレッドへの書き込み数を設定します")
    async def set_threshold_command(self, ctx, threshold: int):
        # チャンネルを取得
        channel = ctx.channel

        # チャンネルを登録
        with get_db() as db:
            config = GuildConfigCrud.find_or_create(db, channel.guild.id)
            GuildConfigCrud.update(db, channel.guild.id, {"thread_list_threshold": threshold})

        # メッセージを送信
        await ctx.respond(
            f"{channel.mention} のスレッドリストの許容するスレッドへの書き込み数を {threshold} に設定しました",
            ephemeral=True)

    @slash_command(name="get_threshold",
                   description="許容するスレッドへの書き込み数を取得します")
    async def get_threshold_command(self, ctx):
        # チャンネルを取得
        channel = ctx.channel

        # チャンネルを登録
        with get_db() as db:
            config = GuildConfigCrud.find_or_create(db, channel.guild.id)

        if config is None or config.thread_list_threshold is None:
            threshold = self.default_threshold
        else:
            threshold = config.thread_list_threshold

        # メッセージを送信
        await ctx.respond(
            f"{channel.mention} のスレッドリストの許容するスレッドへの書き込み数は {threshold} です",
            ephemeral=True)

    @slash_command(name="delete_threshold",
                   description="許容するスレッドへの書き込み数をデフォルトに戻します")
    async def delete_threshold_command(self, ctx):
        # チャンネルを取得
        channel = ctx.channel

        # チャンネルを登録
        with get_db() as db:
            config = GuildConfigCrud.find_or_create(db, channel.guild.id)
            GuildConfigCrud.update(db, config, {"thread_list_threshold": None})

        # メッセージを送信
        await ctx.respond(
            f"{channel.mention} のスレッドリストの許容するスレッドへの書き込み数をデフォルト({self.default_threshold})に戻しました",
            ephemeral=True)

    @slash_command(name="is_target",
                   description="スレッドリストを管理するチャンネルかどうかを判定します")
    async def is_target_command(self, ctx):
        # チャンネルを取得
        channel = ctx.channel

        # メッセージを送信
        await ctx.respond(
            f"{channel.mention} はスレッドリストを管理するチャンネルです" if self.is_target(
                channel) else f"{channel.mention} はスレッドリストを管理するチャンネルではありません",
            ephemeral=True)


def setup(bot):
    return bot.add_cog(ThreadListManager(bot))
