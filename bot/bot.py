import logging

import discord
from discord.ext import commands
import sentry_sdk

from config import bot_config

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s][%(levelname)s] %(message)s"
)

if bot_config.SENTRY_DSN is not None and bot_config.SENTRY_DSN != "":
    sentry_sdk.init(
        dsn=bot_config.SENTRY_DSN,
        traces_sample_rate=1.0
    )
    logging.info("SENTRY is enabled.")
else:
    logging.warning("SENTRY_DSN is not configured.")

if bot_config.TOKEN is None or bot_config.TOKEN == "":
    logging.error("TOKEN is not set.")
    exit(0)

# bot init
bot = commands.Bot(help_command=None,
                   case_insensitive=True,
                   activity=discord.Game("©Yuki Watanabe"),
                   intents=discord.Intents.all()
                   )

bot.load_extension("cogs.Admin")
bot.load_extension("cogs.CogManager")

bot.load_extension("cogs.ThreadListManager")
bot.load_extension("cogs.Reminder")

bot.run(bot_config.TOKEN)
