from discord.ext.commands import errors
from discord.ext import commands
import discord


def setup(bot):
    global settings
    settings = bot.settings
    bot.add_cog(Helper(bot))


async def prefix_base(ctx):
    gid = str(ctx.guild.id)
    if gid not in settings:
        settings[gid] = {}
    if 'prefixes' not in settings[gid]:
        settings[gid]['prefixes'] = settings['default_prefix']


class Helper(commands.Cog):
    """https://github.com/foxnerdsaysmoo/zedutils#helper"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='invite')
    async def invite(self, ctx):
        """Get invite link for ZedUtils"""
        msg = 'To invite ZedUtils, go to: https://discord.com/oauth2/authorize?client_id=746465008967221259&scope=bot'
        await ctx.send(msg)

    @commands.group(name='prefix', invoke_without_command=True)
    async def prefix(self, ctx):
        """
        **Prefix commands**
        prefix
        prefix list
        prefix add [prefix]
        prefix remove [prefix]
        """
        await ctx.invoke(self.list_)

    @prefix.command(name='list')
    async def list_(self, ctx):
        gid = str(ctx.guild.id)
        prefixes = settings['default_prefix']
        if gid in settings:
            if 'prefixes' in settings[gid]:
                prefixes = settings[gid]['prefixes']
        await ctx.send("Prefixes here are:\n`{}`".format('`\n`'.join(prefixes)))

    @prefix.command(name='add', aliases=['new'])
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, *, prefix: str = None):
        if prefix is None:
            raise errors.UserInputError(
                f'Please include a prefix with your command'
            )

        await prefix_base(ctx)

        gid = str(ctx.guild.id)
        settings[gid]['prefixes'].append(prefix)
        settings[gid]['prefixes'] = list(dict.fromkeys(settings[gid]['prefixes']))
        await settings.save()
        await ctx.send(f':white_check_mark: Added `{prefix}` as a new ZedUtils prefix')

    @prefix.command()
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, *, prefix: str = None):
        if prefix is None:
            await ctx.send(
                f'Please add a prefix with your command. `>prefix add [prefix here]`'
            )
            return

        await prefix_base(ctx)

        gid = str(ctx.guild.id)

        if prefix not in settings[gid]['prefixes']:
            raise commands.BadArgument(
                'Given prefix not in prefixes. View current prefixes using `>prefix` or `prefix list`'
            )

        settings[gid]['prefixes'].remove(prefix)
        await settings.save()
        await ctx.send(f':white_check_mark: Removed prefix `{prefix}`')

    @commands.command(name='help')
    async def help(self, ctx, cog: str = None):
        """Show this message"""
        if not cog:
            help_embed = discord.Embed(title='ZedUtil Cog Listings',
                                       description='Use `>help [cog]` to find out more about them!')

            cogs_desc = ''
            for x in self.bot.cogs:
                if not hasattr(self.bot.cogs[x], 'hidden'):
                    cogs_desc += ('[{}]({})'.format(x, self.bot.cogs[x].__doc__) + '\n')
            help_embed.add_field(name='Cogs', value=cogs_desc[0:len(cogs_desc) - 1], inline=False)

            await ctx.send(embed=help_embed)
        else:
            found = False
            for x, i in self.bot.cogs.items():
                if x.lower() == cog.lower():
                    if not hasattr(self.bot.cogs[x], 'hidden'):
                        help_embed = discord.Embed(title=f'{x} Command Listings',
                                                   url=self.bot.cogs[x].__doc__)
                    else:
                        help_embed = discord.Embed(title=f'{x}',
                                                   description=self.bot.cogs[x].__doc__)
                        for c in i.get_commands():
                            if not c.hidden:
                                help_embed.add_field(name=f'{c.name}', value=str(c.help), inline=False)
                    found = True

            if not found:
                raise errors.UserInputError('Invalid cog name')

            await ctx.send(embed=help_embed)
