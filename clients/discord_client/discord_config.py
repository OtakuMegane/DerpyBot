from configparser import ConfigParser
import common
import os

# This file is only code. Don't put settings here! Settings should go in config/discord.cfg

config = common.load_config_from_files([common.CONFIG_DEFAULTS_PATH + 'discord.cfg', common.CONFIG_PATH + 'discord.cfg'])

token = config.get('Config', 'token', fallback = '')
playing = config.get('Config', 'playing', fallback = 'with Markov chains')

owner_ids = []
for owner in config.get('Config', 'owner_ids', fallback = '').split(','):
    owner_ids.append(owner.strip())

command_alias = config.get('Config', 'command_alias', fallback = '!derpy')

channels = []
for channel in config.get('Config', 'channels', fallback = '').split(','):
    print(channel.strip())
    channels.append(channel.strip())

all_channels = config.getboolean('Config', 'all_channels', fallback = False)

markov_channels = []
for channel in config.get('Config', 'markov_channels', fallback = '').split(','):
    markov_channels.append(channel.strip())

markov_all_channels = config.getboolean('Config', 'markov_all_channels', fallback = False)
markov_dms = config.getboolean('Config', 'markov_dms', fallback = True)
chat_to_console = config.getboolean('Config', 'chat_to_console', fallback = True)
ignore_bots = config.getboolean('Config', 'ignore_bots', fallback = True)
raw_to_markov = config.getboolean('Config', 'raw_to_markov', fallback = False)
clean_output = config.getboolean('Config', 'clean_output', fallback = True)
