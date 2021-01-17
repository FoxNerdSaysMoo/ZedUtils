from discord.ext.commands import errors, Cog
from discord.ext import commands
import discord
from discord import Color
import asyncio


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


class Helper(Cog):
    """helper"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='invite')
    async def invite(self, ctx):
        """Get invite link for ZedUtils"""
        embed = discord.Embed(title="Invite ZedUtils",
                              description="[Top.gg](https://top.gg/bot/746465008967221259)",
                              color=Color.from_rgb(230, 230, 230))
        await ctx.send(embed=embed)

    @commands.group(name='prefix', invoke_without_command=True)
    async def prefix(self, ctx):
        """
        Prefix commands
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
                'Please add a prefix with your command. `>prefix add [prefix here]`'
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
                                       description='Use `>help [cog]` to find out more about them!',
                                       color=Color.darker_gray())

            help_embed.set_author(name=f'{ctx.message.content}',
                                  icon_url=ctx.author.avatar_url,
                                  url="https://github.com/foxnerdsaysmoo/zedutils#features")

            cogs_desc = ''
            for x in self.bot.cogs:
                if not hasattr(self.bot.cogs[x], 'hidden'):
                    cogs_desc += '[{}]({})'.format(
                        x,
                        "https://github.com/foxnerdsaysmoo/zedutils#" + self.bot.cogs[x].__doc__
                    ) + '\n'
            help_embed.add_field(name='Cogs', value=cogs_desc[0:len(cogs_desc) - 1], inline=False)

            await ctx.send(embed=help_embed)
        else:
            found = False
            for x, i in self.bot.cogs.items():
                if x.lower() == cog.lower():
                    if not hasattr(self.bot.cogs[x], 'hidden'):
                        url = "https://github.com/foxnerdsaysmoo/zedutils#" + self.bot.cogs[x].__doc__
                        help_embed = discord.Embed(title=f'{x} help',
                                                   url=url,
                                                   color=Color.darker_gray())
                        help_embed.set_author(name=f'{ctx.message.content}',
                                              icon_url=ctx.author.avatar_url,
                                              url=url)
                    else:
                        help_embed = discord.Embed(title=f'{x}',
                                                   description=self.bot.cogs[x].__doc__,
                                                   color=Color.darker_gray())
                    commands_ = ''
                    for c in i.get_commands():
                        if not c.hidden:
                            commands_ += f'**{c.name}** - {c.help}\n'

                    help_embed.add_field(name='Commands', value=commands_)

                    found = True

            if not found:
                raise errors.UserInputError('Invalid cog name')

            await ctx.send(embed=help_embed)

    @Cog.listener()
    async def on_message(self, message):
        if self.bot.user.mentioned_in(message):
            msg = await message.channel.send('You can get my help message using `>help`')
            await asyncio.sleep(settings['msg_timeout'])
            await msg.delete()

    @Cog.listener()
    async def on_guild_join(self, guild):
        settings[str(guild.id)] = {}
        await settings.save()

    @Cog.listener()
    async def on_guild_leave(self, guild):
        settings.pop(str(guild.id))
        await settings.save()
