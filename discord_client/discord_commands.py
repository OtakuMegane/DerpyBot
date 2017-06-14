from configparser import SafeConfigParser
import pkg_resources
import common
import discord
from collections import defaultdict

commands = defaultdict(dict)
markov = None
config = None

def pass_data(markov_instance, discord_config):
    global markov, config
    markov = markov_instance
    config = discord_config

def list_commands():
    command_list = ["__Discord Commands__"]

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
    
    command_output = '**\n**'.join(sorted(command_list))
    markov_commands = markov.get_command_list()
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

    #custom_file = pkg_resources.resource_string(__name__, 'custom_commands.ini')
    config = SafeConfigParser()
    #config.read_string(custom_file.decode())
    config.read("config/custom_discord_commands.ini")
    sections = config.sections()

    for section in sections:
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
    response = None
    rejoined = ' '.join(split_content)

    if 'markov' in split_content[0]:
        split_content.pop(0)
        return markov.incoming_message_command(' '.join(split_content))

    if 'commands' in split_content[0]:
        return list_commands()
    
    if 'reload commands' and message.author.id == config.get('Discord', 'owner_id'):
        load_custom_commands(True)

    for command in commands:
        if rejoined.startswith(command):
            if commands[command]['base_command'] is not None:
                command = commands[command]['base_command']

            return commands[command]['content']

    return None
