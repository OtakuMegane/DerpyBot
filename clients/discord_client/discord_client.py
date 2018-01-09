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

version = '0.9.2.3'

discord_client = discord.Client()
ready = False
markov = None
derpy_stats = None
console_prefix = "[Discord] "

def logged_in():
    return discord_client.is_logged_in

def still_running(print):
    if print:
        common.console_print("Client still running! Logged in? " + logged_in(), console_prefix)
    return True

@discord_client.event
async def on_ready():
    global ready

    common.console_print(" We have logged in to Discord!", console_prefix)
    common.console_print("  Name: " + discord_client.user.name, console_prefix)
    common.console_print("  ID: " + discord_client.user.id, console_prefix)

    try:
        await discord_client.change_presence(game = discord.Game(name = config.discord_playing))
        common.console_print("  Playing: " + config.discord_playing, console_prefix)
    except:
        common.console_print("  Could not set 'Playing' status for some reason.", console_prefix)
        common.console_print(" ", console_prefix)

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

    if message.channel.name not in config.discord_markov_channels:
        markov_learn = False

    if message.channel.is_private:
        common.console_print("Direct Message from " + message.author + ": " + message.content, console_prefix)
    else:
        common.console_print("Message from #" + message.channel.name + ": " + message.content, console_prefix)

    split_content = message.clean_content.split()
    command_check = split_content.pop(0)

    if config.command_alias in command_check:
        reply = discord_commands.get_commands(message, split_content)
    else:
        if markov is not None:
            reply = markov.incoming_message(message.clean_content, discord_client.user.name, markov_learn)

    if reply is not "" and reply is not None:
        if config.chat_to_console:
            if message.channel.is_private:
                common.console_print("Direct Message to " + message.author + ": " + reply, console_prefix)
            else:
                common.console_print("Message to #" + message.channel.name + ": " + reply, console_prefix)

        if isinstance(reply, str):
            await discord_client.send_message(message.channel, reply)
        else:
            await discord_client.send_message(message.channel, embed = reply)

def launch(markov_instance, parent_location, stats_instance):
    global markov, derpy_stats

    config.load(parent_location)
    markov = markov_instance
    derpy_stats = stats_instance
    discord_commands.pass_data(markov, config, stats_instance)  # We'll probably do something better eventually
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
        common.console_print("Logging out...", console_prefix)

        while logged_in():
            time.sleep(0.25)

    common.console_print("We are logged out now!", console_prefix)

def shutdown():
    logout()
    common.console_print("Shutting down client...", console_prefix)
