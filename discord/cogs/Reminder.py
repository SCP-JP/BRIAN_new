from datetime import datetime, timedelta

import discord
from discord.commands import slash_command
from discord.ext import commands, tasks

from config.bot_config import NOTIFY_TO_OWNER
from db.package.crud.remind_target import RemindTargetCrud
from db.package.models import RemindTarget
from db.package.session import get_db


class CreateSnoozeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="スヌーズ", style=discord.ButtonStyle.primary, custom_id="reminder:create_snooze")
    async def create_snooze(self, _: discord.ui.Button, interaction: discord.Interaction):
        remind_message_id = interaction.message.id

        with get_db() as db:
            origin_remind = RemindTargetCrud.get_by_remind_message_id(db, remind_message_id)
            if origin_remind is None:
                return

            RemindTargetCrud.create_snooze(db, origin_remind)

        await interaction.response.edit_message(view=CancelSnoozeView())


class CancelSnoozeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="スヌーズを解除", style=discord.ButtonStyle.danger, custom_id="reminder:cancel_snooze")
    async def cancel_snooze(self, _: discord.ui.Button, interaction: discord.Interaction):
        remind_message_id = interaction.message.id
        with get_db() as db:
            RemindTargetCrud.cancel_snooze(db, remind_message_id)

        await interaction.response.edit_message(view=CreateSnoozeView())


class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.remind_task.stop()
        self.remind_task.start()

        self.bot.add_view(CreateSnoozeView())
        self.bot.add_view(CancelSnoozeView())

    @commands.Cog.listener()
    async def on_message(self, _: discord.Message):
        if not self.remind_task.is_running():
            self.remind_task.start()

    @tasks.loop(seconds=30)
    async def remind_task(self):
        with get_db() as db:
            targets: list[RemindTarget] = RemindTargetCrud.get_targets(db)

            for target in targets:
                channel = self.bot.get_channel(target.channel_id)
                if channel is None:
                    channel = await self.bot.fetch_channel(target.channel_id)
                user = self.bot.get_user(target.user_id)
                if user is None:
                    user = await self.bot.fetch_user(target.user_id)

                if channel is None or user is None:
                    continue

                if target.is_snooze:
                    view = CancelSnoozeView()
                else:
                    view = CreateSnoozeView()

                # target_toがNoneならDMにリマインド
                if target.remind_to is None or target.remind_to == "":
                    # channelがmention属性を持っていたらそれを利用、持っていなかったら省略
                    try:
                        mention = channel.mention
                    except AttributeError:
                        mention = "不明なチャンネル"

                    try:
                        msg = await user.send(f'リマインド： {mention} {f"（{target.note}）" if target.note else ""}',
                                              view=view)
                    except discord.Forbidden:
                        try:
                            msg = await channel.send("\n".join([
                                f"### 【リマインド】",
                                f"作成者： {user.mention}",
                                f"対象者： {mention}",
                                f" {target.note if target.note else ''}"
                            ]), view=view)
                        except discord.Forbidden:
                            await NOTIFY_TO_OWNER(self.bot, f"Forbidden: DM to {user.name}")
                            continue

                # target_toがNoneでないなら作成したチャンネルにリマインド
                else:
                    try:
                        msg = await channel.send("\n".join([
                            f"### 【リマインド】",
                            f"作成者： {user.mention}",
                            f"対象者： {target.remind_to}",
                            f" {target.note if target.note else ''}"
                        ]), view=view)
                    except discord.Forbidden:
                        await NOTIFY_TO_OWNER(self.bot,
                                              f"Forbidden: Send a msg in {channel.mention}")
                        continue

                # リマインドメッセージのIDを保存
                RemindTargetCrud.update_remind_flag(db, target.id, msg.id)

                # スヌーズリマインドを作成
                if target.is_snooze:
                    RemindTargetCrud.create_snooze(db, target)

                # 元メッセージを削除
                if target.previous_remind_message_id:
                    previous_message = await channel.fetch_message(target.previous_remind_message_id)
                    await previous_message.delete()

    @slash_command(name="remind", description="指定した日時にリマインドします")
    async def remind(
            self, ctx,
            after: discord.Option(int, "X時間後にリマインド"),
            target_to: discord.Option(str, "リマインド対象", required=False),
            note: discord.Option(str, "リマインド時に表示するメモ", required=False),
            snooze: discord.Option(bool, "スヌーズを設定するか", required=False, default=False)
    ):
        remind_at = datetime.now() + timedelta(hours=after)
        with get_db() as db:
            RemindTargetCrud.create(db, ctx.author.id, ctx.channel.id, note, remind_at, target_to, snooze)

        await ctx.respond(
            f"{ctx.author.mention} {after}時間後にリマインドします",
            ephemeral=True
        )

    @slash_command(name="list_reminder", description="リマインドリストを表示します")
    async def list_reminder(self, ctx):
        with get_db() as db:
            reminders = RemindTargetCrud.get_user_targets(db, ctx.author.id)

        if not reminders:
            await ctx.respond("リマインドはありません", ephemeral=True)
            return

        embed = discord.Embed(title="リマインドリスト", colour=discord.Colour.teal())
        for reminder in reminders:
            embed.add_field(
                name=f"<t:{int(reminder.remind_at.timestamp())}:R>",
                value=f"<#{reminder.channel_id}>",
                inline=False
            )

        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    return bot.add_cog(Reminder(bot))
