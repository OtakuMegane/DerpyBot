from configparser import ConfigParser
import pkg_resources
import discord
import re
import os
import common
import datetime

custom_commands = {}
custom_commands['triggers'] = {}
custom_commands['data'] = {}
config = common.load_config_file(common.CONFIG_PATH + "discord_commands.cfg")

def list_commands():
    command_list = ["__Discord Custom Commands__"]

    for command_data in custom_commands['data'].values():
        aliased = ""
        description = ""

        if command_data['aliases']:
            aliased = " (aliases: " + ', '.join(command_data['aliases']) + ")"

        if command_data['description']:
            description = "**  " + command_data['description'] + "** "

        command_list.append(command_data['base_command'] + aliased + description)

    command_output = '**\n**'.join(sorted(command_list, key = str.lower))
    markov_commands = common.markov.get_command_list()
    markov_command_list = []

    if markov_commands:
        markov_command_list.append("\n")
        markov_command_list.append("__Markov Commands__ (markov <command>)")

    for command in markov_commands:
        description = ""

        if markov_commands[command]['description']:
            description = "**  " + markov_commands[command]['description'] + "** "

        markov_command_list.append(command + description)

    command_output += '**\n**'.join(sorted(markov_command_list))

    return "**" + command_output + "**"

def load_custom_commands(reload):
    global custom_commands

    if reload:
        custom_commands = {}
        custom_commands['triggers'] = {}
        custom_commands['data'] = {}

    if len(config.sections()) == 0:
        return

    sections = config.sections()

    for section in sections:
        custom_commands['triggers'].update({section:section})
        custom_commands['data'][section] = {}
        custom_commands['data'][section]['base_command'] = section
        custom_commands['data'][section]['aliases'] = []
        custom_commands['data'][section]['content'] = config.get(section, 'content', fallback = '')
        custom_commands['data'][section]['description'] = config.get(section, 'description', fallback = None)

        aliases = config.get(section, 'alias_commands', fallback = None)

        if aliases:
            for alias in aliases.split(','):
                custom_commands['data'][section]['aliases'].append(alias)
                custom_commands['triggers'].update({alias.casefold():section})

def get_commands(message, split_content):
    rejoined = ' '.join(split_content)

    if len(split_content) == 0:
        return None

    if 'markov' in split_content[0]:
        split_content.pop(0)
        return common.markov.incoming_command(' '.join(split_content), False)

    if 'commands' in split_content[0]:
        return list_commands()

    if 'reload commands' in rejoined and message.author.id in common.discord_config.owner_ids:
        load_custom_commands(True)
        return "Custom commands have been reloaded!"

    if 'uptime' in split_content[0]:
        bot_start_time = common.derpybot_stats.retrieve_stats('derpybot', 'start_time')
        uptime_delta = datetime.datetime.now() - bot_start_time
        up_m, up_s = divmod(uptime_delta.seconds, 60)
        up_h, up_m = divmod(up_m, 60)
        up_d = uptime_delta.days
        uptime = "I has been running for: {3} days, {2} hours, {1} minutes, {0} seconds".format(up_s, up_m, up_h, up_d)
        return uptime

    base_command = custom_commands['triggers'].get(rejoined.casefold())

    if base_command:
        return custom_commands['data'][base_command]['content']

    return None
