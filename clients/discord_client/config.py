from configparser import SafeConfigParser

config = SafeConfigParser()
bot_token = ""
discord_playing = ""
owner_id = ""
discord_channels = []
discord_learn_channels = []

def load(parent_location):
    global bot_token, discord_playing, owner_id, discord_channels, discord_learn_channels
    
    config.read(parent_location + '/config/defaults.cfg')
    config.read(parent_location + '/config/config.cfg')
    bot_token = config.get('Discord', 'token')
    discord_playing = config.get('Discord', 'playing')
    owner_id = config.get('Discord', 'owner_id')

    for channel in config.get('Discord', 'channels').split(','):
        discord_channels.append(channel.strip())

    for channel in config.get('Discord', 'learn-channels').split(','):
        discord_learn_channels.append(channel.strip())