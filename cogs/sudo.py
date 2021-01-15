from discord.ext import commands
import discord
from discord.ext.commands import errors


def setup(bot):
    global settings
    settings = bot.settings
    bot.add_cog(Sudo(bot))


class Sudo(commands.Cog):
    """Bot control commands (bot managers only)"""
    def __init__(self, bot):
        self.bot = bot
        self.admins = [515854207837011970]

    @commands.group(name='sudo')
    async def sudo(self, ctx):
        """
        **Bot manager commands**
        sudo status [activity] [value]
        sudo reload
        sudo save
        sudo timeout [value]
        """
        ...

    @sudo.command(name='status')
    async def set_status(self, ctx, act_type: str, *, name: str):
        """Set status of ZedUtils"""
        if ctx.author.id not in self.admins:
            raise errors.NotOwner

        try:
            activity = getattr(discord.ActivityType, act_type.lower())
        except AttributeError:
            raise errors.UserInputError(f"Invalid activity tye: {act_type}")

        await self.bot.change_presence(activity=discord.Activity(type=activity, name=name))
        await ctx.send(':white_check_mark: Successfully changed status!')

    @sudo.command(name='reload')
    async def reload_cogs(self, ctx):
        """Reload cogs without restarting bot"""
        if ctx.author.id not in self.admins:
            raise errors.NotOwner

        for cog in self.bot.cogs_list:
            self.bot.reload_extension(cog)

        await ctx.send(':white_check_mark: Cogs reloaded')

    @sudo.command(name='save')
    async def save_settings(self, ctx):
        """Save ZedUtils settings"""
        if ctx.author.id not in self.admins:
            raise errors.NotOwner

        await settings.save()
        await ctx.send(':white_check_mark: Saved settings')

    @sudo.command(name='set')
    async def set_timout(self, ctx, key: str = None, value: int = None):
        """Set settings value"""
        if ctx.author.id not in self.admins:
            raise errors.NotOwner

        if value is None:
            value = 0
        settings[key] = value
        await ctx.send(f':white_check_mark: Set {key} to {value}')

