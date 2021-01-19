from utils.cooldown import cooldown
from discord.ext.commands import command, Cog, Bot, errors
from discord import User, Embed, Color
from .base_economy import Inventory
import random
import asyncio


def setup(bot: Bot):
    global economy
    economy = bot.economy
    bot.add_cog(Economy(bot))


class Economy(Cog):
    """economy"""
    def __init__(self, bot: Bot):
        self.bot = bot

    @command(name='bank')
    async def bank(self, ctx, user: User = None):
        """View your or another user's economy stats"""
        if user is None:
            user = ctx.author

        if str(user.id) not in economy:
            economy[str(user.id)] = economy['default_economy']
            economy.save()

        stats = economy[str(user.id)]

        embed = Embed(
            title=f'{user}\'s bank',
            color=getattr(Color, stats['color'])() if stats['color'] else Embed.Empty
        )

        embed.add_field(name="Coins", value=stats['coins'])

        medals = f"""
        :military_medal: {stats['medals'][0]}
        :first_place: {stats['medals'][1]}
        :second_place: {stats['medals'][2]}
        :third_place: {stats['medals'][3]}
        """
        embed.add_field(name="Medals", value=medals)

        inventory = Inventory(stats['inventory'], economy['suffixes'])
        embed.add_field(name="Inventory", value=f"{inventory.len()} artifacts")

        boosts = ", ".join([f'{x}x {y}' for y, x in stats['boosts']])
        embed.add_field(name="Boosts", value=boosts if boosts else "None :(")

        active_boosts = ", ".join([f"{y}s of {x}" for x, y in stats['active_boosts']])
        embed.add_field(name="Active boosts", value=active_boosts if active_boosts else "None :(")

        embed.set_author(name='ZedUtils economy',
                         url="https://github.com/foxnerdsaysmoo/zedutils#economy",
                         icon_url=user.avatar_url)

        await ctx.send(embed=embed)

    @command(name='inventory')
    async def inventory(self, ctx, user: User = None):
        if user is None:
            user = ctx.author

        if str(user.id) not in economy:
            economy[str(user.id)] = economy['default_economy']
            economy.save()

        inventory = Inventory(economy[str(user.id)]['inventory'], economy['suffixes'])
        stats = economy[str(user.id)]

        embed = Embed(title=f"{user}'s Inventory",
                      description=str(inventory),
                      color=getattr(Color, stats['color'])() if stats['color'] else Embed.Empty)

        embed.set_author(name='ZedUtils economy',
                         url="https://github.com/foxnerdsaysmoo/zedutils#economy",
                         icon_url=user.avatar_url)

        await ctx.send(embed=embed)

    @command(name='coin-flip')
    async def coin_flip(self, ctx, wager: int):
        """Take a 50-50 chance to win or lose a wager"""
        wager = abs(wager)

        if str(ctx.author.id) not in economy:
            economy[str(ctx.author.id)] = economy['default_economy']

        stats = economy[str(ctx.author.id)]

        if wager > stats['coins']:
            raise errors.UserInputError('Your wager is larger than your coin amount')

        if random.choice([True, False]):
            economy[str(ctx.author.id)]['coins'] += wager

            embed = Embed(
                title="You won!",
                description=f"{ctx.author} now has {economy[str(ctx.author.id)]['coins']} coins",
                color=Color.green()
            )
            await ctx.send(embed=embed)
        else:
            economy[str(ctx.author.id)]['coins'] -= wager

            embed = Embed(
                title="You lost!",
                description=f"{ctx.author} now has {economy[str(ctx.author.id)]['coins']} coins",
                color=Color.red()
            )
            await ctx.send(embed=embed)

    @command(name='work')
    @cooldown(60 * 60)
    async def work(self, ctx):
        """Work to make some money, with a chance of promotion"""
        if str(ctx.author.id) not in economy:
            economy[str(ctx.author.id)] = economy['default_economy']

        stats = economy[str(ctx.author.id)]

        economy[str(ctx.author.id)]['coins'] += stats['salary']

        embed = Embed(title="You went to work and made some 💸",
                      description=f"You made {stats['salary']} coins today",
                      color=Color.green())

        embed.add_field(name="Current salary", value=f"{stats['salary']} coins")
        embed.add_field(name="Total coins", value=stats['coins'])

        await ctx.send(embed=embed)

        if random.choice([False]*11 + [True]):
            economy[str(ctx.author.id)]['salary'] += random.randint(50, 120)
            salary = economy[str(ctx.author.id)]['salary']

            embed = Embed(title="You got promoted!", description=f"Your new salary is {salary}!", color=Color.green())

            await ctx.send(embed=embed)

        elif random.choice([False]*24 + [True]):
            economy[str(ctx.author.id)]['salary'] -= random.randint(40, 130)
            salary = economy[str(ctx.author.id)]['salary']

            embed = Embed(title="You were demoted.", description=f"Your new salary is {salary}.", color=Color.red())

            await ctx.send(embed=embed)

        economy.save()

    @command(name='rob')
    @cooldown(60 * 30)
    async def crime(self, ctx, user: User):
        """Try to steal from a user"""
        if str(user.id) not in economy:
            economy[str(user.id)] = economy['default_economy']
        if str(ctx.author.id) not in economy:
            economy[str(ctx.author.id)] = economy['default_economy']

        stats = economy[str(user.id)]
        percentage = random.randint(5, 30)
        amount = int(stats['coins']*percentage/100)

        if random.choice([False]*5 + [True]*8):
            economy[str(ctx.author.id)]['coins'] += amount
            auth_stats = economy[str(ctx.author.id)]

            embed = Embed(title=f"You stole {amount} coins from {user}!",
                          description=f"You now have {auth_stats['coins']} coins.",
                          color=Color.green())
            await ctx.send('Success!', embed=embed)

        else:
            economy[str(ctx.author.id)]['coins'] -= int(amount * 1.5)
            auth_stats = economy[str(ctx.author.id)]

            embed = Embed(title=f"You were caught stealing! You lost {int(amount * 1.2)} coins!",
                          description=f"You now have {auth_stats['coins']} coins.",
                          color=Color.red())
            await ctx.send('Failure.', embed=embed)

    @Cog.listener('on_ready')
    async def rand_artifacts(self):
        """Randomly summon artifacts"""
        servers = self.bot.guilds
        numservers = len(servers)
        interval_range = economy['interval_range']
        interval = random.randint(*interval_range) / numservers  # How often to summon a artifact
        while True:
            # Wait
            await asyncio.sleep(interval)
            interval = random.randint(*interval_range) / numservers

            selserver = random.choices(servers,
                                       weights=[len(x.members) for x in servers],
                                       k=1)[0]  # Randomly choose a server

            artifact = random.choices(
                list(economy['rand_artifacts'].keys()),
                weights=list(economy['rand_artifacts'].values()),
                k=1,
            )[0]  # Randomly choose a artifact using weights

            embed = Embed(title=f"A {artifact} appeared!",
                          description="React with :white_check_mark: to claim!",
                          color=Color.green())

            msg = await selserver.text_channels[0].send(embed=embed)
            await msg.add_reaction('✅')  # Add checkmark reaction

            def check(reaction, user):
                return user.id != self.bot.user.id and reaction.emoji == '✅' and reaction.message.id == msg.id

            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=economy['rand_item_timeout'])  # Wait for a reaction
            except asyncio.TimeoutError:
                await msg.delete()  # Delete artifact message if it isn't reacted to
                continue

            await msg.delete()  # Delete message

            if str(user.id) not in economy:  # If user doesn't have economy set up
                economy[str(user.id)] = economy['default_economy']

            inv = economy[str(user.id)]['inventory']  # User's inventory
            if artifact in inv:
                inv[artifact] += 1
            else:
                inv[artifact] = 1
            economy.save()  # Save economy

    @command(name='create-artifact', hidden=True)
    async def create_artifact(self, ctx, name: str, weight: int):
        if ctx.author.id not in self.bot.cogs["Sudo"].owners:
            raise errors.NotOwner

        economy["rand_items"][name] = weight
        economy.save()

        await ctx.send(f":white_check_mark: Added artifact '{name}' with weight {weight}.")

    @command(name='suggest-item')
    @cooldown(60 * 60)
    async def suggest_item(self, ctx, name: str, weight: int):
        pass

