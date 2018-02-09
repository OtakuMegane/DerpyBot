from threading import Thread
from configparser import SafeConfigParser
import common
import time
import importlib
import importlib.util
import re
import os
import datetime

version = '0.9.3.3'

script_location = os.path.dirname(os.path.abspath(__file__))
config = SafeConfigParser(allow_no_value = True)
config.read(script_location + '/config/defaults.cfg')
config.read(script_location + '/config/config.cfg')

markov = None
use_discord_client = common.set_boolean(config.get('Config', 'use_discord_client'))
use_markov = common.set_boolean(config.get('Config', 'use_markov'))
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
            common.console_print("Client logged in: " + str(chat_client.logged_in()), console_prefix)

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

def shutdown():
    global shutting_down
    shutting_down = True
    common.console_print("Shutting everything down...", console_prefix)

    if not markov.shutting_down:
        markov.shutdown()

    chat_client.shutdown()
    common.console_print("Good night!", console_prefix)
    raise SystemExit

stats_module_load()
common.console_print("DerpyBot version " + version, console_prefix)
markov_load(False)
client_load(False)

while not chat_client.ready:
    time.sleep(0.1)

status_thread = Thread(target = client_status, args = [])
status_thread.start()
derpy_stats.add_new_set('derpybot')
derpy_stats.update_stats('derpybot', 'start_time', datetime.datetime.now())
commands()
