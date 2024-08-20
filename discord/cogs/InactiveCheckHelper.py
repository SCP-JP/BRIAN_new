import discord
from discord import Message
from discord.commands import slash_command
from discord.ext import commands


class InactiveCheckHelper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_last_message(self, member: discord.Member) -> Message:
        last_message = None
        async for message in member.history(limit=1):
            last_message = message
        return last_message

    @slash_command(name="check_last_message", description="特定ロールに属するユーザの最終メッセージを確認します")
    @commands.has_permissions(administrator=True)
    async def check_last_message_command(self, ctx, role: discord.Option(discord.Role, "確認するロール")):
        await ctx.respond(f"{role.name} に属するユーザの最終メッセージを確認します", ephemeral=True)

        res = []

        for member in role.members:
            last_message = await self.get_last_message(member)
            if last_message is not None:
                res.append(
                    f"{member.mention} : {last_message.created_at.strftime('%Y-%m-%d %H:%M:%S')} : {last_message.content[:50]}"
                )
            else:
                res.append(f"{member.mention} : メッセージがありません")

        await ctx.respond("\n".join(res), ephemeral=True)


def setup(bot):
    return bot.add_cog(InactiveCheckHelper(bot))
