from discord.ext import commands
from utils import settings, prefix
import os
import discord

intents = discord.Intents().all()


class Bot(commands.Bot):
    settings['default_prefix'] = ['>']
    settings['msg_timeout'] = 5
    settings['chess_challenge_timeout'] = 20

    def __init__(self):
        super(Bot, self).__init__(command_prefix=prefix.prefix(settings), intents=intents)

        self.remove_command('help')

        self.settings = settings

        self.cogs_list = [
            "cogs.sudo",
            "cogs.chatter",
            "cogs.helper",
            "cogs.errors",
            "cogs.games.chess",
            "cogs.utils",
            "cogs.games.economy",
        ]

        for cog in self.cogs_list:
            self.load_extension(cog)

    async def on_ready(self):
        print(f'Logged in as {self.user.name} | {self.user.id}')


bot = Bot()
bot.run(os.getenv('ZEDUTILS_TOKEN'))
