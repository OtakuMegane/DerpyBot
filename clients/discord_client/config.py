from configparser import ConfigParser
import common
import os

# config.py is just code. Don't put settings here!
# Settings should go in config.cfg

script_location = os.path.dirname(os.path.abspath(__file__))
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

    config = ConfigParser()
    common.load_config_file(parent_location + '/config/defaults.cfg', config)
    common.load_config_file(parent_location + '/config/config.cfg', config)

    if config.has_section('Discord'):
        command_alias = config.get('Discord', 'command_alias', fallback = '!derpy')
        bot_token = config.get('Discord', 'token', fallback = '')
        discord_playing = config.get('Discord', 'playing', fallback = '')

        for owner in config.get('Discord', 'owner_ids', fallback = '').split(','):
            owner_ids.append(owner.strip())

        chat_to_console = config.getboolean('Discord', 'chat-to-console', fallback = True)

        for channel in config.get('Discord', 'channels', fallback = '').split(','):
            discord_channels.append(channel.strip())

        for channel in config.get('Discord', 'markov-channels', fallback = '').split(','):
            discord_markov_channels.append(channel.strip())

        if config.has_option('Markov', 'markov_learn_pm'): # Legacy
            markov_learn_dm = config.getboolean('Markov', 'markov_learn_pm', fallback = True)
        else:
            markov_learn_dm = config.getboolean('Markov', 'markov_learn_dm', fallback = True)
