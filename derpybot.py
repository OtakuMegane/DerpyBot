from threading import Thread
from configparser import ConfigParser
import common
import derpybot_config
import chat_clients
import importlib
import importlib.util
import re

import datetime
import pathlib

import hikari
import os

version = '0.9.3.12'
config = ConfigParser(allow_no_value = True)

markov = None
derpy_stats = None
status_thread = None
shutting_down = False
console_prefix = "[DerpyBot]"

def commands():
    common.console_print("Entering command mode...", console_prefix)

    while not shutting_down:
        command = input('>> ')

        if command == "":
            continue

        split_command = command.split()
        
        if len(split_command) > 1:
            command_target = split_command.pop(0)
            command = split_command.pop(0)
            arguments = split_command
        else:
            command_target = ""
            command = split_command.pop(0)
            arguments = []
        
        if "client" in command_target:
            console_client_commands(command, arguments)
            continue

        if "markov" in command_target:
            markov.incoming_console_command(command)
            continue

        if command == "shutdown":
            shutdown()

        if command == "reload markov":
            markov_load(True)
            
def console_client_commands(command, arguments):
    if command == "status":
            chat_clients.get_client(arguments[0]).running(True)

    if command == "start":
            chat_clients.start(arguments[0])

    if command == "stop":
            chat_clients.stop(arguments[0])

def markov_load(reload):
    global markov

    if not derpybot_config.use_derpymarkov:
        return

    common.console_print("Loading markov...", console_prefix)

    return
    if reload:
        importlib.reload(markov)
    else:
        markov_package = config.get('Markov', 'markov_package')
        markov_module = config.get('Markov', 'markov_module')
        markov = importlib.import_module('modules.' + markov_package + '.' + markov_module)

    markov.activate(reload)
    common.markov = markov

def stats_module_load():
    global derpy_stats

    derpy_stats = importlib.import_module('derpy_stats')
    derpy_stats.add_new_set('derpybot')
    derpy_stats.update_stats('derpybot', 'start_time', datetime.datetime.now())
    
def load_config():
    global config

    defaults_present = False
    common.load_config_file(common.CONFIG_PATH + 'defaults.cfg', config)

    if len(config.sections()) != 0:
        defaults_present = True

    common.load_config_file(common.CONFIG_PATH + 'config.cfg', config)
    
    if not defaults_present and len(config.sections()) == 0:
        common.console_print("Both configuration files config.cfg and defaults.cfg are missing or empty! D:", console_prefix)
        common.console_print("We can't function like this...", console_prefix)
        shutdown()

def load_clients():
    if derpybot_config.load_discord_client:
        chat_clients.start('discord')
    
def shutdown():
    global shutting_down
    shutting_down = True
    common.console_print("Shutting everything down...", console_prefix)

    if markov is not None:
        if not markov.shutting_down:
            markov.shutdown()

    chat_clients.shutdown()
    status_thread.join(1)
    common.console_print("Good night!", console_prefix)
    raise SystemExit

#load_config()
stats_module_load()
common.console_print("DerpyBot version " + version, console_prefix)
markov_load(False)
load_clients()
status_thread = Thread(target = chat_clients.monitor, args = [])
status_thread.start()
commands()
