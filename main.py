from discord.ext import commands
from utils import settings, prefix
import os
import discord
import json
import atexit


economy = settings("data/economy.json")
auctionhouse = settings("data/auctions.json")
settings = settings("data/settings.json")

atexit.register(economy.save)
atexit.register(settings.save)
atexit.register(auctionhouse.save)

intents = discord.Intents().all()

with open("data/config.json", "r") as readfile:
    config = json.load(readfile)

settings.update(config)
economy.update(config)


class Bot(commands.Bot):
    def __init__(self):
        super(Bot, self).__init__(command_prefix=prefix.prefix(settings), intents=intents)

        self.remove_command('help')

        self.settings = settings
        self.economy = economy
        self.auctionhouse = auctionhouse

        self.cogs_list = [
            "cogs.sudo",
            "cogs.chatter",
            "cogs.helper",
            "cogs.errors",
            "cogs.games.chess",
            "cogs.utils",
            "cogs.games.economy.economy",
            "cogs.games.economy.auction",
            "cogs.games.economy.shop"
        ]

        for cog in self.cogs_list:
            self.load_extension(cog)

    async def on_ready(self):
        print(f'Logged in as {self.user.name} | {self.user.id}')


bot = Bot()
bot.run(os.getenv('ZEDUTILS_TOKEN'))
