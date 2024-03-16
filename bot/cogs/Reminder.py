from datetime import datetime, timedelta

import discord
from discord.commands import slash_command
from discord.ext import commands, tasks

from db.crud.remind_target import RemindTargetCrud
from db.session import get_db


class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.remind_task.stop()
        self.remind_task.start()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not self.remind_task.is_running():
            self.remind_task.start()

    @tasks.loop(seconds=60)
    async def remind_task(self):
        with get_db() as db:
            targets = RemindTargetCrud.get_targets(db)

            for target in targets:
                channel = self.bot.get_channel(target.channel_id)
                if channel is None:
                    channel = await self.bot.fetch_channel(target.channel_id)
                user = self.bot.get_user(target.user_id)
                if user is None:
                    user = await self.bot.fetch_user(target.user_id)

                if channel is None or user is None:
                    continue

                await user.send(f'リマインド： {channel.mention} {f"（{target.note}）" if target.note else ""}')

                RemindTargetCrud.update_remind_flag(db, target.id)

    @slash_command(name="remind", description="指定した日時にリマインドします")
    async def remind(
            self, ctx,
            after: discord.Option(int, "X時間後にリマインド"),
            note: discord.Option(str, "リマインド時に表示するメモ", required=False),
    ):
        remind_at = datetime.now() + timedelta(hours=after)
        with get_db() as db:
            remind_target = RemindTargetCrud.create(db, ctx.author.id, ctx.channel.id, note, remind_at)

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
