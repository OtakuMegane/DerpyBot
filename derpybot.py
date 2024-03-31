from threading import Thread
from configparser import ConfigParser
import common
import derpybot_config
import chat_clients
import importlib
import re
import datetime
import pathlib
import os

version = '0.9.3.12'
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
            common.markov.incoming_console_command(command)
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
    if not derpybot_config.use_derpymarkov:
        return

    common.console_print("Loading markov...", console_prefix)

    if reload:
        importlib.reload(common.markov)
    else:
        common.markov = importlib.import_module('modules.derpymarkov.markov')

    common.markov.activate(reload)

def stats_module_load():
    #global derpy_stats

    #derpy_stats = importlib.import_module('derpy_stats')
    common.derpybot_stats.add_new_set('derpybot')
    common.derpybot_stats.update_stats('derpybot', 'start_time', datetime.datetime.now())

def load_clients():
    if derpybot_config.load_discord_client:
        chat_clients.start('discord')
    
def shutdown():
    global shutting_down
    shutting_down = True
    common.console_print("Shutting everything down...", console_prefix)

    if common.markov is not None:
        if not common.markov.shutting_down:
            common.markov.shutdown()

    chat_clients.shutdown()
    status_thread.join(1)
    common.console_print("Good night!", console_prefix)
    raise SystemExit

stats_module_load()
common.console_print("DerpyBot version " + version, console_prefix)
markov_load(False)
load_clients()
status_thread = Thread(target = chat_clients.monitor, args = [])
status_thread.start()
commands()
