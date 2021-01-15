import discord
from discord.ext import commands
from discord.ext.commands import errors
import pyttsx3
import asyncio


def setup(bot):
    global settings
    settings = bot.settings
    bot.add_cog(Chatter(bot))


class Chatter(commands.Cog):
    """"""
    def __init__(self, bot):
        self.bot = bot
        self.volume = 1.0
        self.rate = 200

    @commands.command(name='connect')
    async def connect_(self, ctx, channel: discord.VoiceChannel = None):
        """"""
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise errors.ChannelNotFound('No channel to join. Please either join or specify a channel.')

        await ctx.send(f'Connecting to **`{channel.name}`**')
        await channel.connect()

        while ctx.author.voice is not None:
            await asyncio.sleep(2)

        try:
            for vc in self.bot.voice_clients:
                if vc.guild == ctx.guild:
                    await vc.disconnect()
        except Exception as e:
            print(type(e).__name__, e)

    @commands.command(name='disconnect')
    async def disconnect(self, ctx):
        """Make ZedUtils leave a voice channel"""
        try:
            ctx.author.voice.channel
        except AttributeError:
            raise errors.ChannelNotFound('You are not in a channel with me. Join a channel to use this command')

        for vc in self.bot.voice_clients:
            if vc.guild == ctx.guild:
                await vc.disconnect()
                return

        raise errors.ChannelNotFound('I am not connected to a voice channel on this server. Use `>connect` to summon me')

    @commands.command(name='say')
    async def say_tts(self, ctx):
        """Tell ZedUtils to say a phrase/word"""
        msg = ctx.message.content[ctx.message.content.find('say') + 4:]

        if len(msg) > 50 and ctx.author.id not in self.bot.get_cog('Sudo').admins:
            raise errors.BadArgument('Message is too long!')

        engine = pyttsx3.init()
        if ctx.guild.id in settings:
            server_settings = settings[ctx.guild.id]
            engine.setProperty('rate', server_settings['rate'] if 'rate' in server_settings else self.rate)
            engine.setProperty('volume', server_settings['volume'] if 'volume' in server_settings else self.volume)
        else:
            engine.setProperty('rate', self.rate)
            engine.setProperty('volume', self.volume)

        engine.save_to_file(msg, 'test.mp3')
        engine.runAndWait()
        while engine.isBusy():
            await asyncio.sleep(0.05)

        voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if not voice_client:
            await ctx.send('Not connected to voice channel! You must use `>connect` before using this command')
            return

        player = discord.FFmpegPCMAudio('test.mp3')

        print(f'Playing \'{msg}\'... ', end='')
        playing = await ctx.message.reply(f'Playing \'{msg}\'', mention_author=True)

        voice_client.play(player, after=lambda a: voice_client.stop())

        print('done')
        await asyncio.sleep(settings['msg_timout'])
        await playing.delete()

    @commands.command(name='rate')
    async def rate_cmd(self, ctx, rate: int = None):
        """
        rate
        View current rate
        rate [value]
        set rate to value (value must be > 80 and < 300)
        """
        if rate is None:
            rate = self.rate
            if ctx.guild.id in settings:
                if 'rate' in settings[ctx.guild.id]:
                    rate = settings[ctx.guild.id]['rate']
            await ctx.send(f'Current voice rate is {rate} wpm')
            return

        if not 80 < rate < 300:
            raise errors.UserInputError(f'Invalid rate of {rate}!')

        gid = str(ctx.guild.id)
        if gid not in settings:
            settings[gid] = {'rate': rate}
        else:
            settings[gid]['rate'] = rate
        settings.save()
        await ctx.send(f':white_check_mark: Voice rate changed to {rate} wpm')

