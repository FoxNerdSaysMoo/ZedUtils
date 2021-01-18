from utils.cooldown import cooldown
from discord.ext.commands import command, Cog, Bot, errors
from discord import User, Embed, Color
import random
import asyncio


def setup(bot: Bot):
    global settings
    settings = bot.settings
    settings['default_economy'] = {
        'coins': 0,
        'medals': (0, 0, 0, 0),
        'boosts': [],
        'active_boosts': [],
        'color': None,
        'salary': 500,
        'inventory': [],
    }

    settings['rand_items'] = [
        ["Unicorn horn", 30],
        ["Police cruiser", 60],
        ["Brick", 100],
        ["Diamond ring", 35]
    ]

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

        if str(user.id) not in settings[str(ctx.guild.id)]:
            settings[str(ctx.guild.id)][str(user.id)] = settings['default_economy']
            await settings.save()

        stats = settings[str(ctx.guild.id)][str(user.id)]

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

        inventory = "\n".join([f'{x}x {y}' for y, x in stats['inventory']])
        embed.add_field(name="Inventory", value=inventory if inventory else "None :(")

        boosts = ", ".join([f'{x}x {y}' for y, x in stats['boosts']])
        embed.add_field(name="Boosts", value=boosts if boosts else "None :(")

        active_boosts = ", ".join([f"{y}s of {x}" for x, y in stats['active_boosts']])
        embed.add_field(name="Active boosts", value=active_boosts if active_boosts else "None :(")

        embed.set_author(name='ZedUtils economy',
                         url="https://github.com/foxnerdsaysmoo/zedutils#economy",
                         icon_url=user.avatar_url)

        await ctx.send(embed=embed)

    @command(name='coin-flip')
    async def coin_flip(self, ctx, wager: int):
        """Take a 50-50 chance to win or lose a wager"""
        wager = abs(wager)

        if str(ctx.author.id) not in settings[str(ctx.guild.id)]:
            settings[str(ctx.guild.id)][str(ctx.author.id)] = settings['default_economy']

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

    @command(name='work')
    @cooldown(60 * 60)
    async def work(self, ctx):
        """Work to make some money, with a chance of promotion"""
        if str(ctx.author.id) not in settings[str(ctx.guild.id)]:
            settings[str(ctx.guild.id)][str(ctx.author.id)] = settings['default_economy']

        stats = settings[str(ctx.guild.id)][str(ctx.author.id)]

        settings[str(ctx.guild.id)][str(ctx.author.id)]['coins'] += stats['salary']

        embed = Embed(title="You went to work and made some 💸",
                      description=f"You made {stats['salary']} coins today",
                      color=Color.green())

        embed.add_field(name="Current salary", value=f"{stats['salary']} coins")
        embed.add_field(name="Total coins", value=stats['coins'])

        await ctx.send(embed=embed)

        if random.choice([False]*11 + [True]):
            settings[str(ctx.guild.id)][str(ctx.author.id)]['salary'] += random.randint(50, 120)
            salary = settings[str(ctx.guild.id)][str(ctx.author.id)]['salary']

            embed = Embed(title="You got promoted!", description=f"Your new salary is {salary}!", color=Color.green())

            await ctx.send(embed=embed)

        elif random.choice([False]*24 + [True]):
            settings[str(ctx.guild.id)][str(ctx.author.id)]['salary'] -= random.randint(40, 150)
            salary = settings[str(ctx.guild.id)][str(ctx.author.id)]['salary']

            embed = Embed(title="You were demoted.", description=f"Your new salary is {salary}.", color=Color.red())

            await ctx.send(embed=embed)

    @command(name='crime')
    @cooldown(60 * 30)
    async def crime(self, ctx, user: User):
        """Try to steal from a user"""
        if str(user.id) not in settings[str(ctx.guild.id)]:
            settings[str(ctx.guild.id)][str(user.id)] = settings['default_economy']
        if str(ctx.author.id) not in settings[str(ctx.guild.id)]:
            settings[str(ctx.guild.id)][str(ctx.author.id)] = settings['default_economy']

        stats = settings[str(ctx.guild.id)][str(user.id)]
        percentage = random.randint(0, 20)
        amount = int(stats['coins']*percentage/100)

        if random.choice([False]*5 + [True]*7):
            settings[str(ctx.guild.id)][str(ctx.author.id)]['coins'] += amount
            auth_stats = settings[str(ctx.guild.id)][str(ctx.author.id)]

            embed = Embed(title=f"You stole {amount} coins from {user}!",
                          description=f"You now have {auth_stats['coins']} coins.",
                          color=Color.green())
            await ctx.send('Success!', embed=embed)

        else:
            settings[str(ctx.guild.id)][str(ctx.author.id)]['coins'] -= int(amount * 1.2)
            auth_stats = settings[str(ctx.guild.id)][str(ctx.author.id)]

            embed = Embed(title=f"You were caught stealing! You lost {int(amount * 1.2)} coins!",
                          description=f"You now have {auth_stats['coins']} coins.",
                          color=Color.red())
            await ctx.send('Failure.', embed=embed)

    @Cog.listener('on_ready')
    async def rand_items(self):
        """Randomly summon items"""
        servers = self.bot.guilds
        numservers = len(servers)
        interval = random.randint(200, 400) / numservers  # How often to summon a item
        while True:
            # Wait
            await asyncio.sleep(interval)
            interval = random.randint(200, 400) / numservers

            selserver = random.choice(servers)  # Randomly choose a server

            item = random.choices(
                [x for x, y in settings['rand_items']],
                weights=[y for x, y in settings['rand_items']],
                k=1,
            )[0]  # Randomly choose a item using weights

            embed = Embed(title=f"A {item} appeared!",
                          description="React with :white_check_mark: to claim!",
                          color=Color.green())

            msg = await selserver.text_channels[0].send(embed=embed)  # Send the item embed | Needs improvement
            await msg.add_reaction('✅')  # Add checkmark reaction

            def check(reaction, user):
                return user.id != self.bot.user.id and reaction.emoji == '✅' and reaction.message.id == msg.id

            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=15)  # Wait for a reaction
            except asyncio.TimeoutError:
                await msg.delete()  # Delete item message if it isn't reacted to
                continue

            await msg.delete()  # Delete message

            if str(user.id) not in settings[str(selserver.id)]:  # If user doesn't have economy set up
                settings[str(selserver.id)][str(user.id)] = settings['default_economy']

            inv = settings[str(selserver.id)][str(user.id)]['inventory']  # User's inventory
            if item in inv:  # Add item counter if it it already in inventory
                settings[str(selserver.id)][str(user.id)]['inventory'][inv.index(item)][1] += 1
            else:  # Create slot of not in inventory
                settings[str(selserver.id)][str(user.id)]['inventory'].append([item, 1])

            await settings.save()  # Save settings
