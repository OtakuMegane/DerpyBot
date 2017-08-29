import asyncio
import discord
import threading
import time
from configparser import SafeConfigParser
import importlib
from . import discord_commands
from . import config
import os
import common

version = '0.9.2'

discord_client = discord.Client()
ready = False
markov = None
console_prefix = "[Discord] "

def logged_in():
    return discord_client.is_logged_in

def still_running(print):
    if print:
        common.console_print(console_prefix, "Client still running! Logged in? " + logged_in())
    return True

@discord_client.event
async def on_ready():
    global ready

    common.console_print(console_prefix, " We have logged in to Discord!")
    common.console_print(console_prefix, "  Name: " + discord_client.user.name)
    common.console_print(console_prefix, "  ID: " + discord_client.user.id)

    try:
        await discord_client.change_presence(game = discord.Game(name = config.discord_playing))
        common.console_print(console_prefix, "  Playing: " + config.discord_playing)
    except:
        common.console_print(console_prefix, "  Could not set 'Playing' status for some reason.")
        common.console_print(console_prefix, " ")

    ready = True

@discord_client.event
async def on_message(message):
    reply = None
    markov_learn = True

    if message.channel.name not in config.discord_channels:
        return

    if message.author.bot or message.author == discord_client.user:
        return

    if message.content is "" or message.content is None:
        return

    if message.channel.name not in config.discord_learn_channels:
        markov_learn = False

    if message.channel.is_private:
        common.console_print(console_prefix, "Direct Message from " + message.author + ": " + message.content)
    else:
        common.console_print(console_prefix, "Message from #" + message.channel.name + ": " + message.content)

    split_content = message.clean_content.split()
    command_check = split_content.pop(0)

    if '!derpy' in command_check:
        reply = discord_commands.get_commands(message, split_content)
    else:
        if markov is not None:
            reply = markov.incoming_message(message.clean_content, discord_client.user.name, markov_learn)

    if reply is not "" and reply is not None:
        if message.channel.is_private:
            common.console_print(console_prefix, "Direct Message to " + message.author + ": " + reply)
        else:
            common.console_print(console_prefix, "Message to #" + message.channel.name + ": " + reply)

        if isinstance(reply, str):
            await discord_client.send_message(message.channel, reply)
        else:
            await discord_client.send_message(message.channel, embed = reply)

def launch(markov_instance, parent_location):
    global markov
    
    config.load(parent_location)
    markov = markov_instance
    discord_commands.pass_data(markov, config)  # We'll probably do something better eventually
    discord_commands.load_custom_commands(False, parent_location)

    try:
        discord_client.loop.run_until_complete(discord_client.start(config.bot_token))
    except KeyboardInterrupt:
        discord_client.loop.run_until_complete(discord_client.logout())
        pending = asyncio.Task.all_tasks(loop = discord_client.loop)
        gathered = asyncio.gather(*pending, loop = discord_client.loop)
        try:
            gathered.cancel()
            discord_client.loop.run_until_complete(gathered)
            gathered.exception()
        except:
            pass

def logout():
    if logged_in():
        future = asyncio.run_coroutine_threadsafe(discord_client.logout(), discord_client.loop)
        common.console_print(console_prefix, "Logging out...")

        while logged_in():
            time.sleep(0.25)

    common.console_print(console_prefix, "We are logged out now!")

def shutdown():
    logout()
    common.console_print(console_prefix, "Shutting down client...")
