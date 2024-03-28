from configparser import ConfigParser
import pkg_resources
import discord
import re
import os
from collections import defaultdict
import common
import datetime

commands = defaultdict(dict)
config = common.load_config_file(common.CONFIG_PATH + "custom_discord_commands.cfg")
derpy_stats = None

def list_commands():
    command_list = []

    for command in commands:
        if commands[command]['base_command'] is None:
            command_list.append(command)
            aliased = ""
            description = ""

            if commands[command]['aliases'] is not None:
                aliased = " (aliases: " + ', '.join(commands[command]['aliases']) + ")"

            if commands[command]['description'] is not None:
                description = "**  " + commands[command]['description'] + "** "

            command_list[command_list.index(command)] = command + aliased + description

    command_list.insert(0, "__Discord Commands__")
    command_output = '**\n**'.join(sorted(command_list, key = str.lower))
    markov_commands = common.markov.get_command_list()
    markov_command_list = []

    if markov_commands:
        markov_command_list.append("\n")
        markov_command_list.append("__Markov Commands__ (markov <command>)")

    for command in markov_commands:
        description = ""

        if markov_commands[command]['description'] is not None:
            description = "**  " + markov_commands[command]['description'] + "** "

        markov_command_list.append(command + description)

    command_output += '**\n**'.join(sorted(markov_command_list))

    return "**" + command_output + "**"

def load_custom_commands(reload):
    global commands

    if reload:
        commands = defaultdict(dict)

    if len(config.sections()) == 0:
        return

    sections = config.sections()

    for section in sections:
        if config.has_option(section, 'content'):
            commands[section]['content'] = config.get(section, 'content')

        commands[section]['base_command'] = None
        commands[section]['aliases'] = None
        commands[section]['description'] = None

        if config.has_option(section, 'alias_commands'):
            alternates = config.get(section, 'alias_commands').split(',')
            commands[section]['aliases'] = alternates

            for alternate in alternates:
                alternate = alternate.strip()
                commands[alternate]['base_command'] = section

        if config.has_option(section, 'description'):
            commands[section]['description'] = config.get(section, 'description')

def get_commands(message, split_content):
    rejoined = ' '.join(split_content)

    if len(split_content) == 0:
        return None

    if 'markov' in split_content[0]:
        split_content.pop(0)
        return common.markov.incoming_message_command(' '.join(split_content))

    if 'commands' in split_content[0]:
        return list_commands()

    if 'reload commands' in rejoined and message.author.id in config.owner_ids:
        load_custom_commands(True)
        return "Commands have been reloaded!"

    if 'uptime' in split_content[0]:
        bot_start_time = common.derpy_stats.retrieve_stats('derpybot', 'start_time')
        uptime_delta = datetime.datetime.now() - bot_start_time
        up_m, up_s = divmod(uptime_delta.seconds, 60)
        up_h, up_m = divmod(up_m, 60)
        up_d = uptime_delta.days
        uptime = "I has been running for: {3} days, {2} hours, {1} minutes, {0} seconds".format(up_s, up_m, up_h, up_d)
        return uptime

    for command in commands:
        if re.match(re.escape(command) + r'([^\w]|$)', rejoined) is not None:
            if commands[command]['base_command'] is not None:
                command = commands[command]['base_command']

            return commands[command]['content']

    return None
