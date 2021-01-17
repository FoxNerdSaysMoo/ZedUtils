from discord.ext.commands import command, Cog, Bot, has_permissions, errors
from discord import User, Embed, Color
import random


def setup(bot: Bot):
    global settings
    settings = bot.settings
    bot.add_cog(Economy(bot))


default = {
    'coins': 0,
    'medals': (0, 0, 0, 0),
    'boosts': [],
    'active_boosts': [],
    'color': None
}


class Economy(Cog):
    """economy"""
    def __init__(self, bot: Bot):
        self.bot = bot

    @command(name='bank')
    async def bank(self, ctx, user: User = None):
        """View your or another user's economy stats"""
        if user is None:
            user = ctx.author

        if user.id not in settings[str(ctx.guild.id)]:
            settings[str(ctx.guild.id)][str(user.id)] = default
            await settings.save()

        stats = settings[str(ctx.guild.id)][str(user.id)]

        embed = Embed(
            title=f'{user}\'s bank',
            description="\u200b",
            color=getattr(Color, stats['color']) if stats['color'] else Embed.Empty
        )

        embed.add_field(name="Coins", value=stats['coins'])

        medals = f"""
        :military_medal: {stats['medals'][0]}
        :first_place: {stats['medals'][1]}
        :second_place: {stats['medals'][2]}
        :third_place: {stats['medals'][3]}
        """
        embed.add_field(name="Medals", value=medals)

        boosts = ", ".join([f'{x}x{y}' for y, x in stats['boosts']])
        embed.add_field(name="Boosts", value=boosts if boosts else "None :(")

        active_boosts = ", ".join([f"{y}s of {x}" for x, y in stats['active_boosts']])
        embed.add_field(name="Active boosts", value=active_boosts if active_boosts else "None :(")

        embed.set_author(name='ZedUtils economy',
                         url="https://github.com/foxnerdsaysmoo/zedutils#economy",
                         icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)

    @command(name='coin-give', aliases=['coins-give', 'coin-add', 'coins-add'])
    @has_permissions(administrator=True)
    async def coin_give(self, ctx, user: User, amount: int):
        """Give coins to a user"""
        if str(user.id) not in settings[str(ctx.guild.id)]:
            settings[str(ctx.guild.id)][str(user.id)] = default

        settings[str(ctx.guild.id)][str(user.id)]['coins'] += abs(amount)

        embed = Embed(title="Coins added",
                      description=f"{user} now has {settings[str(ctx.guild.id)][str(user.id)]['coins']} coins",
                      color=Color.green())

        await ctx.send(embed=embed)

    @command(name='coin-remove', aliases=['coins-remove', 'coin-take'])
    @has_permissions(administrator=True)
    async def coin_remove(self, ctx, user: User, amount: int):
        """Remove coins from user"""
        if str(user.id) not in settings[str(ctx.guild.id)]:
            settings[str(ctx.guild.id)][str(user.id)] = default

        settings[str(ctx.guild.id)][str(user.id)]['coins'] -= abs(amount)

        embed = Embed(title="Coins removed",
                      description=f"{user} now has {settings[str(ctx.guild.id)][str(user.id)]['coins']} coins",
                      color=Color.red())

        await ctx.send(embed=embed)

    @command(name='coin-flip')
    async def coin_flip(self, ctx, wager: int):
        """Take a 50-50 chance to win or lose a wager"""
        wager = abs(wager)

        if str(ctx.author.id) not in settings[str(ctx.guild.id)]:
            settings[str(ctx.guild.id)][str(ctx.author.id)] = default

        stats = settings[str(ctx.guild.id)][str(ctx.author.id)]

        if wager > stats['coins']:
            raise errors.UserInputError('Your wager is larger than your coin amount')

        if random.choice([True, False]):
            settings[str(ctx.guild.id)][str(ctx.author.id)]['coins'] += wager

            embed = Embed(
                title="You won!",
                description=f"{ctx.author} now has {settings[str(ctx.guild.id)][str(ctx.author.id)]['coins']} coins",
                color=Color.green()
            )
            await ctx.send(embed=embed)
        else:
            settings[str(ctx.guild.id)][str(ctx.author.id)]['coins'] -= wager

            embed = Embed(
                title="You lost!",
                description=f"{ctx.author} now has {settings[str(ctx.guild.id)][str(ctx.author.id)]['coins']} coins",
                color=Color.red()
            )
            await ctx.send(embed=embed)
