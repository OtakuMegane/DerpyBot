from configparser import SafeConfigParser
import common

config = SafeConfigParser()
bot_token = ""
discord_playing = ""
owner_id = ""
discord_channels = []
discord_markov_channels = []
chat_to_console = None
#TODO: config.has_section, sanity checks

def load(parent_location):
    global bot_token, discord_playing, owner_id, discord_channels, discord_learn_channels, chat_to_console
    
    config.read(parent_location + '/config/defaults.cfg')
    config.read(parent_location + '/config/config.cfg')
    bot_token = config.get('Discord', 'token')
    discord_playing = config.get('Discord', 'playing')
    owner_id = config.get('Discord', 'owner_id')
    chat_to_console = common.set_boolean(config.get('Discord', 'chat-to-console'))

    for channel in config.get('Discord', 'channels').split(','):
        discord_channels.append(channel.strip())

    for channel in config.get('Discord', 'learn-channels').split(','):
        discord_markov_channels.append(channel.strip())