import importlib
import time
from threading import Thread
import common

clients = {}
client_threads = {}
monitored_clients = {}
shutting_down = False
console_prefix = "[DerpyBot]"

def get_client(id):
    global clients

    client = clients.get(id)

    if client is None:
        if id == 'discord':
            client = importlib.import_module('clients.discord_client.discord_client')

        clients[id] = client

    return client

def start(id):
    client = get_client(id)

    if client is None or client.running(False):
        return

    if not client.startup_check():
        common.console_print("Client failed startup checks.", console_prefix)
        return

    importlib.reload(client)
    client_threads[id] = Thread(target = client.start, args = [])
    client_threads.get(id).start()
    monitored_clients[id] = client

def stop(id):
    global monitored_clients

    client = get_client(id)
    client.stop()
    del monitored_clients[id]

def monitor():
    while not shutting_down:
        time.sleep(5.0)

        for id, client in monitored_clients.items():
            if client is not None and not shutting_down and not client.running(False):
                start(client.type())

def shutdown():
    global shutting_down

    shutting_down = True

    for id, client in clients.items():
        client.stop()
