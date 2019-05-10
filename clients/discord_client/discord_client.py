import asyncio
import discord
import threading
import time
from configparser import ConfigParser
import importlib
from . import discord_commands
from . import config
import os
import common

version = '0.9.2.10'

discord_client = discord.Client()
discordpy_legacy = discord.version_info[0] < 1
ready = False
markov = None
derpy_stats = None
console_prefix = "[Discord Client] "
logged_in = False

def logged_in():
    return logged_in

def still_running(print):
    if print:
        common.console_print("Client still running! Logged in? " + str(logged_in()), console_prefix)
    return True

@discord_client.event
async def on_ready():
    global ready

    common.console_print(" We have logged in to Discord!", console_prefix)
    common.console_print("  Name: " + discord_client.user.name, console_prefix)
    common.console_print("  ID: " + str(discord_client.user.id), console_prefix)

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
    markov_learn = False
    bot_mentioned = discord_client.user in message.mentions

    if message.author.bot or message.author == discord_client.user:
        return

    if message.content is "" or message.content is None:
        return

    if discordpy_legacy:
        is_private = message.channel.is_private
    else:
        is_private = isinstance(message.channel, discord.abc.PrivateChannel)

    if is_private:
        markov_learn = config.markov_learn_dm
        bot_mentioned = True
        common.console_print("Direct Message from " + message.author.name + ": " + message.content, console_prefix)
    else:
        if message.channel.name not in config.discord_channels:
            return
        if message.channel.name in config.discord_markov_channels:
            markov_learn = True

        common.console_print("Message from #" + message.channel.name + ": " + message.content, console_prefix)

    split_content = message.clean_content.split()
    command_check = split_content.pop(0)

    if config.command_alias == command_check:
        reply = discord_commands.get_commands(message, split_content)
    else:
        if markov is not None:
            reply = markov.incoming_message(message.clean_content, discord_client.user.name, bot_mentioned, markov_learn)

    if reply is not "" and reply is not None:
        if config.chat_to_console:
            if is_private:
                common.console_print("Direct Message to " + message.author.name + ": " + reply, console_prefix)
            else:
                common.console_print("Message to #" + message.channel.name + ": " + reply, console_prefix)

        if isinstance(reply, str):
            if discordpy_legacy:
                await discord_client.send_message(message.channel, reply)
            else:
                await message.channel.send(reply)
        else:
            if discordpy_legacy:
                await discord_client.send_message(message.channel, embed = reply)
            else:
                await message.channel.send(embed = reply)

@discord_client.event
async def on_channel_update(before, after):
    if after.name != before.name:
        if before.name in config.discord_channels and after.name not in config.discord_channels:
            config.discord_channels.append(after.name)
        
        if before.name in config.discord_markov_channels and after.name not in config.discord_markov_channels:
            config.discord_markov_channels.append(after.name)
            
        common.console_print("Channel #" + before.name + " has changed to #" + after.name, console_prefix)

def launch(markov_instance, parent_location, stats_instance):
    global markov, derpy_stats

    common.console_print("Discord Client version " + version, console_prefix)
    config.load(parent_location)
    markov = markov_instance
    derpy_stats = stats_instance
    discord_commands.pass_data(markov, config, stats_instance)  # We'll probably do something better eventually
    discord_commands.load_custom_commands(False, parent_location)

    try:
        asyncio.set_event_loop(discord_client.loop)
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
    future = asyncio.run_coroutine_threadsafe(discord_client.close(), discord_client.loop)
    common.console_print("Logging out...", console_prefix)

def shutdown():
    if logged_in:
        logout()
    common.console_print("Shutting down client...", console_prefix)
