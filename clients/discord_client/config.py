from configparser import ConfigParser
import common

# config.py is just code. Don't put settings here!
# Settings should go in config.cfg

config = ConfigParser()
bot_token = ""
discord_playing = ""
owner_ids = []
command_alias = ""
discord_channels = []
discord_markov_channels = []
markov_learn_dm = True
chat_to_console = True

def load(parent_location):
    global bot_token, discord_playing, owner_ids, command_alias, discord_channels, discord_markov_channels, chat_to_console, markov_learn_dm

    config.read(parent_location + '/config/defaults.cfg')
    config.read(parent_location + '/config/config.cfg')
    
    if config.has_section('Discord'):
        command_alias = config.get('Discord', 'command_alias')
        bot_token = config.get('Discord', 'token')
        discord_playing = config.get('Discord', 'playing')

        for owner in config.get('Discord', 'owner_ids').split(','):
            owner_ids.append(owner.strip())

            chat_to_console = common.set_boolean(config.get('Discord', 'chat-to-console'))

        for channel in config.get('Discord', 'channels').split(','):
            discord_channels.append(channel.strip())

        for channel in config.get('Discord', 'markov-channels').split(','):
            discord_markov_channels.append(channel.strip())
        
        if config.has_option('Markov', 'markov_learn_pm'): # Legacy
            markov_learn_dm = common.set_boolean(config.get('Markov', 'markov_learn_pm'))
        else:
            markov_learn_dm = common.set_boolean(config.get('Markov', 'markov_learn_dm'))
