from threading import Thread
from configparser import ConfigParser
import common
import time
import importlib
import importlib.util
import re
import os
import datetime
import pathlib

version = '0.9.3.10'

script_location = os.path.dirname(os.path.abspath(__file__))
config = ConfigParser(allow_no_value = True)

markov = None
chat_client = None
derpy_stats = None
client_thread = None
status_thread = None
shutting_down = False
console_prefix = "[DerpyBot] "

def commands():
    common.console_print("Entering command mode...", console_prefix)

    while not shutting_down:
        command = input('>> ')

        if command is "":
            continue

        split_command = command.split()
        command_target = split_command.pop(0)
        sub_command = ' '.join(split_command)

        if "markov" in command_target:
            markov.incoming_console_command(sub_command)

        if command == "client status":
            chat_client.still_running(True)

        if command == "client reload":
            client_load(True)

        if command == "client logout":
            chat_client.logout()

        if command == "client shutdown":
            chat_client.shutdown()

        if command == "shutdown":
            shutdown()

        if command == "reload markov":
            markov_load(True)

def client_status():
    global chat_client
    delay = 0

    while not shutting_down:
        time.sleep(1.0)

        if delay < 60:
            delay += 1
            continue

        client_ok = chat_client.still_running(False)

        if not client_ok:
            client_load(True)

def client_load(reload):
    global chat_client, client_thread

    common.console_print("Loading chat client...", console_prefix)

    if reload:
        chat_client.shutdown()
        importlib.reload(chat_client)
    else:
        if use_discord_client:
            chat_client = importlib.import_module('clients.discord_client.discord_client')

    client_thread = None
    client_thread = Thread(target = chat_client.launch, args = ([markov, script_location, derpy_stats]))
    client_thread.start()

def markov_load(reload):
    global markov

    if not use_markov:
        return

    common.console_print("Loading markov...", console_prefix)

    if reload:
        importlib.reload(markov)
    else:
        markov_package = config.get('Markov', 'markov_package')
        markov_module = config.get('Markov', 'markov_module')
        markov = importlib.import_module('modules.' + markov_package + '.' + markov_module)

    markov.activate(reload)

def stats_module_load():
    global derpy_stats

    derpy_stats = importlib.import_module('derpy_stats')
    
def load_config():
    global config

    defaults_present = False
    common.load_config_file(script_location + '/config/defaults.cfg', config)

    if len(config.sections()) is not 0:
        defaults_present = True

    common.load_config_file(script_location + '/config/config.cfg', config)
    
    if not defaults_present and len(config.sections()) is 0:
        common.console_print("Both configuration files config.cfg and defaults.cfg are missing or empty! D:", console_prefix)
        common.console_print("We can't function like this...", console_prefix)
        shutdown()

def shutdown():
    global shutting_down
    shutting_down = True
    common.console_print("Shutting everything down...", console_prefix)

    if markov is not None:
        if not markov.shutting_down:
            markov.shutdown()

    if chat_client is not None:
        chat_client.shutdown()

    common.console_print("Good night!", console_prefix)
    raise SystemExit

load_config()
use_discord_client = config.getboolean('Config', 'use_discord_client', fallback = True)
use_markov = config.getboolean('Config', 'use_markov', fallback = True)
stats_module_load()
common.console_print("DerpyBot version " + version, console_prefix)
markov_load(False)
client_load(False)

while not chat_client.ready and not chat_client.run_failure:
    time.sleep(0.1)

status_thread = Thread(target = client_status, args = [])
status_thread.start()
derpy_stats.add_new_set('derpybot')
derpy_stats.update_stats('derpybot', 'start_time', datetime.datetime.now())
commands()
