import asyncio
import discord
import threading
import time
from configparser import ConfigParser
import importlib
from . import discord_commands
from . import config
from discord.ext import commands
from . import utils
import os
import common
import hikari

version = '0.9.2.13'
config = common.load_config_file(common.CONFIG_PATH + "config.cfg")
token = config.get('Discord', 'token')
client = hikari.GatewayBot(token)
discord_client = discord.Client()
discordpy_legacy = discord.version_info[0] < 1
ready = False
console_prefix = "[Discord Client] "
logged_in = False
loop = None

def type():
    return 'discord'

def running(print):
    if print:
        if client.is_alive:
            common.console_print("Client is online.", console_prefix)
        else:
            common.console_print("Client is offline.", console_prefix)

    return client.is_alive

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

    if message.author.bot and config.ignore_bots:
        return

    if message.author == discord_client.user:
        return

    if message.content == "" or message.content is None:
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
        if not config.discord_all_channels and message.channel.name not in config.discord_channels:
            return

        if config.discord_markov_all_channels or message.channel.name in config.discord_markov_channels:
            markov_learn = True

        common.console_print("Message from #" + message.channel.name + ": " + message.content, console_prefix)

    split_content = message.clean_content.split()
    command_check = split_content.pop(0)

    if config.command_alias == command_check:
        reply = discord_commands.get_commands(message, split_content)
    else:
        if common.markov is not None:
            if config.raw_to_markov:
                markov_text = message.content
            else:
                markov_text = message.clean_content

            reply = common.markov.incoming_message(markov_text, discord_client.user.name, bot_mentioned, markov_learn)

    if reply != "" and reply is not None:
        if config.clean_output:
            reply = utils.clean_mentions(reply, discord_client)

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

def start():
    global loop

    if client.is_alive:
        return

    common.console_print("Starting Discord client version " + version + "...", console_prefix)
    discord_commands.load_custom_commands(False)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(client.start())

def stop():
    if not client.is_alive:
        return

    common.console_print("Shutting down Discord client...", console_prefix)
    loop.run_until_complete(client.close())

