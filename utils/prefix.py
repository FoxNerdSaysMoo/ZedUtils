def prefix(settings):
    def prefix_(client, message):
        if message.guild.id in settings:
            if 'prefixes' in settings[message.guild.id]:
                return settings[message.guild.id]['prefixes']
        return settings['default_prefix']
    return prefix_
