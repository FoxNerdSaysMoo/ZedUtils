import datetime
from discord.ext import commands

on_cooldown = {}


def cooldown(seconds):
    def predicate(context):
        if (cooldown_end := on_cooldown.get(context.author.id)) is None or cooldown_end < datetime.datetime.now():
            if context.valid and context.invoked_with in (*context.command.aliases, context.command.name):
                on_cooldown[context.author.id] = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
            return True
        else:
            raise commands.CommandOnCooldown(commands.BucketType.user, (cooldown_end - datetime.datetime.now()).seconds)

    return commands.check(predicate)
