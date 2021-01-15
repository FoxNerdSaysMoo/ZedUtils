import chess
import chess.svg
from cairosvg import svg2png
from discord.ext.commands import Cog, Bot, Context, command
from discord import Embed, Member, Color, File
import os
import asyncio


def setup(bot: Bot):
    global settings
    settings = bot.settings
    bot.add_cog(Chess(bot))


class Chess(Cog):
    """https://github.com/foxnerdsaysmoo/zedutils#chess"""
    def __init__(self, bot: Bot):
        self.bot = bot
        self.max_games = 10
        self.active_games = {}

    @command(name='chess', aliases=['challenge', 'playchess'])
    async def chess(self, ctx: Context, opponent: Member):
        embed = Embed(title=f'{str(ctx.author)} has challenged {str(opponent)}',
                      description=f'''React to accept the challenge
                      **{settings["chess_challenge_timeout"]} seconds to accept**''')
        chal = await ctx.send('A challenge has been made', embed=embed)
        await chal.add_reaction('✅')
        await chal.add_reaction('❌')

        def react(reaction, user):
            return user.id == opponent.id and str(reaction) in ['❌', '✅']

        try:
            reaction, user = await self.bot.wait_for('reaction_add',
                                                     check=react,
                                                     timeout=settings["chess_challenge_timeout"])
        except asyncio.TimeoutError:
            await ctx.send(
                embed=Embed(title=f'{str(opponent)} did not accept the challenge in time',
                            color=Color.red()))
            return

        if str(reaction) == '❌' or reaction is None:
            embed = Embed(
                title="Challenge declined",
                description=f"{opponent.mention} did not accept the challenge",
                color=Color.red()
            )
            await ctx.send(embed=embed)
            return
        elif str(reaction) == '✅':
            embed = Embed(
                title="Challenge accepted!",
                description=f"""
                {opponent.mention} accepted {ctx.author.mention}'s challenge.
                
                **Loading game...**
                """,
                color=Color.green()
            )
            await ctx.send(embed=embed)

        board = chess.Board()
        curr_player = ctx.author

        def valid_move(message):
            try:
                move = chess.Move.from_uci(message.content)
            except ValueError:
                return False
            return message.author.id == curr_player.id and board.is_legal(move)

        svg2png(bytestring=chess.svg.board(board), write_to=f'chess/{ctx.channel.id}.png')
        await ctx.send(f"{str(curr_player)}'s turn!", file=File(f'chess/{ctx.channel.id}.png'))

        while 1:
            try:
                msg = await self.bot.wait_for('message', check=valid_move, timeout=300.0)
            except asyncio.TimeoutError:
                await ctx.send(
                    f"{str(ctx.author if curr_player != ctx.author else opponent)} has won because their opponent "
                    f"took too long to move"
                )

            board.push(chess.Move.from_uci(msg.content))

            over = board.is_game_over(claim_draw=True)
            if over:
                if board.is_stalemate():
                    await self.stalemate(board, ctx)
                elif board.is_checkmate():
                    await self.checkmate(board, ctx, ctx.author, opponent)

            curr_player = ctx.author if curr_player != ctx.author else opponent

            svg2png(bytestring=chess.svg.board(board), write_to=f'chess/{ctx.channel.id}.png')
            await ctx.send(f"{str(curr_player)}'s turn!" if not over else '', file=File(f'chess/{ctx.channel.id}.png'))

            if over:
                os.remove(f'chess/{ctx.channel.id}.png')
                break

    async def stalemate(self, board, ctx):
        embed = Embed(
            title="Stalemate!",
            description=f"```\n{', '.join([str(i) for i in board.move_stack])}```",
            color=Color.light_grey()
        )
        await ctx.send(embed=embed)

    async def checkmate(self, board, ctx, p1, p2):
        result = board.result()
        winner = p1 if result == '1-0' else p2
        embed = Embed(
            title=f"Checkmate by {str(winner)}!",
            description=f"```\n{', '.join([str(i) for i in board.move_stack])}```",
            color=Color.from_rgb(60, 219, 35)
        )
        await ctx.send(embed=embed)
