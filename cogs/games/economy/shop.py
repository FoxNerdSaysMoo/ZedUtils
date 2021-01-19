from discord.ext.commands import Cog, Bot, group, errors
from discord import Embed, Color


def setup(bot: Bot):
    global economy
    economy = bot.economy
    bot.add_cog(Shop(bot))


class Shop(Cog):
    """shop"""
    def __init__(self, bot: Bot):
        self.bot = bot

    @group(name="shop", invoke_without_command=True)
    async def shop(self, ctx):
        ...

    @group(name="buy", invoke_without_command=True)
    async def buy(self, ctx):
        ...

    @shop.command(name="colors", aliases=["color"])
    async def colors(self, ctx):
        embed = Embed(title="Buy colors",
                      description="Colors for your economy embeds",
                      color=Color.random())
        
        for color, price in economy["embed_colors"].items():
            embed.add_field(name=color, value=str(price)+" coins")

        await ctx.send(embed=embed)

    @buy.command(name="colors", aliases=["color"])
    async def buy_color(self, ctx, color: str):
        colors = economy["embed_colors"]
        if not color in colors:
            raise errors.UserInputError("Invalid color. Use `shop colors` to view available colors")
        
        if str(ctx.author.id) not in economy:
            economy[str(ctx.author.id)] = economy["default_economy"]
        
        price = colors[color]
        if price > economy[str(ctx.author.id)]['coins']:
            raise errors.UserInputError("You don't have enough coins for this color!")
        
        economy[str(ctx.author.id)]['coins'] -= price
        economy[str(ctx.author.id)]['color'] = color

        await ctx.send(
            embed=Embed(title=f"You have bought the embed color `{color}`",
                        color=getattr(Color, color)())
        )
