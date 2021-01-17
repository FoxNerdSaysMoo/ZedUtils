from discord.ext.commands import Bot, Context, errors, Cog
from discord import Color, Embed
import textwrap


def setup(bot):
    bot.add_cog(ErrorHandler(bot))


async def send_error_embed(ctx: Context, message: str):
    embed = Embed(
        title='`{}`'.format(ctx.message.content[:240]),
        description=message,
        color=Color.red()
    )
    await ctx.send('An error occurred while processing your command!', embed=embed)


class ErrorHandler(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.hidden = True

    @Cog.listener()
    async def on_command_error(self, ctx: Context, exception):
        if isinstance(exception, errors.UserInputError):
            await self.handle_user_input_error(ctx, exception)
            return
        elif isinstance(exception, errors.CommandNotFound):
            return
        elif isinstance(exception, errors.CheckFailure):
            await self.handle_check_failure(ctx, exception)
            return
        elif isinstance(exception, errors.CommandOnCooldown):
            await self.handle_cooldown_error(ctx, exception)
            return

        await send_error_embed(
            ctx,
            f"""Your command caused an unknown error. Please report this to the bot owner, or open an issue at this 
            project's [github repo](https://github.com/foxnerdsaysmoo/zedutils).
            
            **Error:**
            ```\n{type(exception).__name__}: {str(exception)}```
            """
        )

    async def handle_user_input_error(self, ctx: Context, exception: errors.UserInputError) -> None:
        command = ctx.command
        parent = command.full_parent_name

        command_name = str(command) if not parent else f"{parent} {command.name}"
        command_syntax = f"```{command_name} {command.signature}```"

        aliases = [f"`{alias}`" if not parent else f"`{parent} {alias}`" for alias in command.aliases]
        aliases = ", ".join(sorted(aliases))

        command_help = f"*{command.help}*" if command.help else ''

        await send_error_embed(
            ctx,
            textwrap.dedent(
                f"""
                __**Invalid Command Usage**__
                
                Your command usage is incorrect: **{exception}**
                
                **Command syntax**
                {command_syntax}
                {"**Command Description**" if command_help or aliases else ""}
                {command_help}
                {f"Aliases: {aliases}" if aliases else ""}
                """
            )
        )

    async def handle_check_failure(self, ctx: Context, exception: errors.CheckFailure) -> None:
        if isinstance(exception, errors.NotOwner):
            msg = "❌ This command is only available to bot owners."
        else:
            msg = "❌ You don't have permission to run this command."
        await send_error_embed(
            ctx,
            msg
        )

    async def handle_cooldown_error(self, ctx: Context, exception: errors.CommandOnCooldown):
        await send_error_embed(
            ctx,
            "This command is on cooldown for another {} seconds. Please try again later.".format(exception.retry_after)
        )
