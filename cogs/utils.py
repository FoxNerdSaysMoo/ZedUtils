from discord.ext.commands import Bot, Context, errors, Cog, command, group, has_permissions
from discord import Color, Embed, Member, Role


def setup(bot: Bot):
    global settings
    settings = bot.settings
    bot.add_cog(Utils(bot))


class Utils(Cog):
    """utils"""
    def __init__(self, bot: Bot):
        self.bot = bot

    @command(name='pfp')
    async def pfp(self, ctx: Context, user: Member = None):
        """Get user's pfp"""
        if user is None:
            user = ctx.author
        await ctx.send(f'{str(user)}\'s pfp')
        await ctx.send(user.avatar_url)

    @group(name='rr')
    @has_permissions(administrator=True)
    async def rr(self, ctx):
        """Create and manage reaction roles"""
        ...

    @rr.command(name='create')
    async def create(self, ctx: Context, name: str):
        embed = Embed(
            title=name
        )
        embed.set_author(
            name='Reaction roles',
            icon_url=ctx.guild.icon_url,
            url='https://github.com/foxnerdsaysmoo/zedutils'
        )
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @rr.command(name='add')
    async def add(self, ctx: Context, emoji: str, option_name: str, role: Role):
        if ctx.message.reference is None:
            raise errors.UserInputError('You must reply to a reaction role embed to use this command')

        msg = await ctx.fetch_message(ctx.message.reference.message_id)

        if msg.author.id != self.bot.user.id:
            raise errors.UserInputError('`rr add` can only be used on messages sent by ZedUtils')

        embed = msg.embeds[0]

        if embed.description:
            embed.description += f'\n{str(emoji)} {option_name}'
        else:
            embed.description = f'\n{str(emoji)} {option_name}'

        await msg.edit(embed=embed)
        await msg.add_reaction(emoji)

        await ctx.message.delete()

        def is_emoji(reaction, user):
            return reaction.emoji == emoji

        while True:
            reaction, user = await self.bot.wait_for('reaction_add', check=is_emoji)
            await Member.add_roles(user, role)
