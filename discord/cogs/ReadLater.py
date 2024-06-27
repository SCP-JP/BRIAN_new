import discord
from discord.ext import commands

from config.bot_config import NOTIFY_TO_OWNER
from db.package.crud.read_later import ReadLaterCrud
from db.package.session import get_db


class ReadLaterListPager(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    def get_page(self, interaction):
        embeds = interaction.message.embeds
        if len(embeds) == 0:
            return 1
        last_embed = embeds[-1]
        return int(last_embed.footer.text)

    @discord.ui.button(label="<<", style=discord.ButtonStyle.primary, custom_id="read_later:pager:back")
    async def back(self, _: discord.ui.Button, interaction: discord.Interaction):
        target_message_id = interaction.message.id

        # 最後のembedからページ数を取得
        page = self.get_page(interaction)

        # pageが1以下の場合は何もしない
        if page <= 1:
            await interaction.respond("最初のページです", ephemeral=True)

        # embedsを更新
        with get_db() as db:
            read_later_messages = ReadLaterCrud.find_all_undone_by_user_id(db, interaction.user.id)

        embeds = await ReadLater.create_list_embeds(interaction.client, read_later_messages, page - 1)
        await interaction.response.edit_message(embeds=embeds)

    @discord.ui.button(label="Reload", style=discord.ButtonStyle.secondary, custom_id="read_later:pager:reload")
    async def reload(self, _: discord.ui.Button, interaction: discord.Interaction):
        with get_db() as db:
            read_later_messages = ReadLaterCrud.find_all_undone_by_user_id(db, interaction.user.id)

        page = self.get_page(interaction)

        embeds = await ReadLater.create_list_embeds(interaction.client, read_later_messages, page)
        await interaction.response.edit_message(embeds=embeds)

    @discord.ui.button(label=">>", style=discord.ButtonStyle.primary, custom_id="read_later:pager:next")
    async def next(self, _: discord.ui.Button, interaction: discord.Interaction):
        target_message_id = interaction.message.id

        # 最後のembedからページ数を取得
        page = self.get_page(interaction)

        # pageが最大ページ数以下の場合は何もしない
        with get_db() as db:
            read_later_messages = ReadLaterCrud.find_all_undone_by_user_id(db, interaction.user.id)

        total_pages = len(read_later_messages) // 5 + 1
        if page >= total_pages:
            await interaction.respond("最後のページです", ephemeral=True)

        # embedsを更新
        embeds = await ReadLater.create_list_embeds(interaction.client, read_later_messages, page + 1)
        await interaction.response.edit_message(embeds=embeds)


class ReadLater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(ReadLaterListPager())

    @staticmethod
    async def create_list_embeds(bot, read_later_messages, page: int = 1, per_page: int = 5):
        embeds = []
        if not read_later_messages or len(read_later_messages) == 0:
            return embeds

        total_pages = len(read_later_messages) // per_page + 1

        if total_pages < page:
            return embeds

        target_messages = read_later_messages[(page - 1) * per_page:page * per_page]

        for target in target_messages:
            channel = bot.get_channel(target.channel_id)
            if channel is None:
                try:
                    channel = await bot.fetch_channel(target.channel_id)
                except (discord.Forbidden, discord.NotFound):
                    continue

            message = await channel.fetch_message(target.message_id)

            content = message.content if len(message.content) < 150 else message.content[:150]
            if len(content) == 0:
                content = "メッセージ内容がありません"

            embed = discord.Embed(title=f"#{channel.name}",
                                  color=discord.Color.blue(),
                                  url=message.jump_url,
                                  timestamp=target.created_at
                                  )
            embed.set_author(
                name=message.author.display_name,
                icon_url=message.author.avatar.url
            )
            embed.add_field(
                name=channel.guild.name,
                value=content,
                inline=False
            )
            embeds.append(embed)

        if len(embeds) > 0:
            embeds[-1].set_footer(text=str(page))
        return embeds

    @commands.message_command(
        name="Add to 'Read Later'",
        name_localizations={
            "ja": "「後で見る」に追加"
        }
    )
    async def read_later(self, ctx: discord.ApplicationContext, message: discord.Message):
        with get_db() as db:
            ReadLaterCrud.create(db, ctx.author.id, message.guild.id, message.channel.id, message.id)

        await ctx.respond("メッセージを「後で見る」に保存しました", ephemeral=True)

    @commands.message_command(
        name="Remove from 'Read Later'",
        name_localizations={
            "ja": "「後で見る」から削除"
        }
    )
    async def remove_read_later(self, ctx: discord.ApplicationContext, message: discord.Message):
        with get_db() as db:
            read_later_message = ReadLaterCrud.find_by_message(db, ctx.author.id,
                                                               message.guild.id, message.channel.id,
                                                               message.id)
            if read_later_message is None:
                await ctx.respond("「後で見る」リストに登録されていません", ephemeral=True)
                return

            ReadLaterCrud.delete(db, read_later_message.id)

        await ctx.respond("メッセージを「後で見る」から削除しました", ephemeral=True)

    @commands.user_command(
        name="Show 'Read Later' List",
        name_localizations={
            "ja": "「後で見る」リストを表示"
        }
    )
    async def read_later_list(self, ctx: discord.ApplicationContext, member: discord.User | discord.Member):
        with get_db() as db:
            read_later_messages = ReadLaterCrud.find_all_undone_by_user_id(db, ctx.author.id)

        embeds = await ReadLater.create_list_embeds(self.bot, read_later_messages)

        if len(embeds) == 0:
            await ctx.respond("「後で見る」リストは空です", ephemeral=True)
            return

        try:
            await ctx.author.send(f"## 「後で見る」リスト", embeds=embeds, view=ReadLaterListPager())
            await ctx.respond("「後で見る」リストをDMで送信しました", ephemeral=True)
        except discord.Forbidden:
            await NOTIFY_TO_OWNER(self.bot, f"送信権限なし: {ctx.author.mention} にメッセージを送信できませんでした")
            pass


def setup(bot):
    return bot.add_cog(ReadLater(bot))
