from discord.ext.commands import Bot, Context, errors, Cog, command, group, has_permissions
from discord import Embed, Member, Role, utils


def setup(bot: Bot):
    global settings
    settings = bot.settings
    bot.add_cog(Utils(bot))


class Utils(Cog):
    """utils"""
    def __init__(self, bot: Bot):
        self.bot = bot
        if 'reaction_roles' not in settings:
            settings['reaction_roles'] = {}

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
        """Create reaction role embed"""
        embed = Embed(
            title=name
        )
        embed.set_author(
            name='Reaction roles',
            icon_url=ctx.guild.icon_url,
            url='https://github.com/foxnerdsaysmoo/zedutils'
        )
        msg = await ctx.send(embed=embed)
        await ctx.message.delete()
        settings['reaction_roles'][str(msg.id)] = []
        await settings.save()

    @rr.command(name='add')
    async def add(self, ctx: Context, emoji: str, option_name: str, role: Role):
        """Add role to reaction role embed"""
        if ctx.message.reference is None:
            raise errors.UserInputError('You must reply to a reaction role embed to use this command')

        msg = await ctx.fetch_message(ctx.message.reference.message_id)

        if msg.author.id != self.bot.user.id:
            raise errors.UserInputError('`rr add` can only be used on messages sent by ZedUtils')

        embed = msg.embeds[0]

        if embed.description:
            if str(emoji) in embed.description:
                parts = embed.description.split('\n')
                description = ''
                for part in parts:
                    if not part.startswith(str(emoji)):
                        description += part
                embed.description = description

            embed.description += f'\n{emoji} {option_name}'
        else:
            embed.description = f'\n{emoji} {option_name}'

        await msg.edit(embed=embed)
        await msg.add_reaction(emoji)

        await ctx.message.delete()

        settings['reaction_roles'][str(msg.id)].append([emoji, role.id])
        await settings.save()

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        reaction = payload.emoji
        msg_id = str(payload.message_id)

        if msg_id in settings['reaction_roles'].keys():
            rr_settings = settings['reaction_roles'][msg_id]

            if str(reaction) in dict(rr_settings).keys():
                guild = self.bot.get_guild(payload.guild_id)
                user = guild.get_member(payload.user_id)

                await Member.add_roles(user, utils.get(guild.roles, id=dict(rr_settings)[str(reaction)]))
