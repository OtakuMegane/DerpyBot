from configparser import ConfigParser
import common
import os

# This file is only code. Don't put settings here! Settings should go in config/derpybot.cfg

config = common.load_config_from_files([common.CONFIG_DEFAULTS_PATH + 'derpybot.cfg', common.CONFIG_PATH + 'derpybot.cfg'])
load_discord_client = config.getboolean('Config', 'load_discord_client', fallback = True)
use_derpymarkov = config.getboolean('Config', 'use_derpymarkov', fallback = True)
