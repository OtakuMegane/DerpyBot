import asyncio
import discord
import time
from . import discord_commands
from . import discord_config
from discord.ext import commands
from . import utils
import os
import common

version = '0.9.2.13'
intents = discord.Intents(guilds = True, messages = True)
discord_client = discord.Client()
discordpy_legacy = discord.version_info[0] < 1
ready = False
console_prefix = "[Discord Client]"
loop = None
is_running = False

def type():
    return 'discord'

def running(print):
    if print:
        if is_running:
            common.console_print("Client is online.", console_prefix)
        else:
            common.console_print("Client is offline.", console_prefix)

    return is_running

@discord_client.event
async def on_ready():
    common.console_print(" We have logged in to Discord!", console_prefix)
    common.console_print("  Name: " + discord_client.user.name, console_prefix)
    common.console_print("  ID: " + str(discord_client.user.id), console_prefix)

    try:
        playing = discord.Game(discord_config.playing)
        await discord_client.change_presence(activity = playing)
        common.console_print("  Playing: " + discord_config.playing, console_prefix)
    except:
        common.console_print("  Could not set 'Playing' status for some reason.", console_prefix)

@discord_client.event
async def on_message(message):
    reply = None
    markov_learn = False
    bot_mentioned = discord_client.user in message.mentions

    if message.author.bot and discord_config.ignore_bots:
        return

    if message.author == discord_client.user:
        return

    if message.content == "" or message.content is None:
        print("empty? " + message.content)
        return

    if discordpy_legacy:
        is_private = message.channel.is_private
    else:
        is_private = isinstance(message.channel, discord.abc.PrivateChannel)

    if is_private:
        markov_learn = discord_config.markov_dms
        bot_mentioned = True
        common.console_print("Direct Message from " + message.author.name + ": " + message.content, console_prefix)
    else:
        print(message.channel.name)
        if not discord_config.all_channels and message.channel.name not in discord_config.channels:
            return

        if discord_config.markov_all_channels or message.channel.name in discord_config.markov_channels:
            markov_learn = True

        common.console_print("Message from #" + message.channel.name + ": " + message.content, console_prefix)

    split_content = message.clean_content.split()
    command_check = split_content.pop(0)

    if discord_config.command_alias == command_check:
        reply = discord_commands.get_commands(message, split_content)
    else:
        if common.markov is not None:
            if discord_config.raw_to_markov:
                markov_text = message.content
            else:
                markov_text = message.clean_content

            reply = common.markov.incoming_message(markov_text, discord_client.user.name, bot_mentioned, markov_learn)

    if reply != "" and reply is not None:
        if discord_config.clean_output:
            reply = utils.clean_mentions(reply, discord_client)

        if discord_config.chat_to_console:
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
        if before.name in discord_config.channels and after.name not in discord_config.channels:
            discord_config.channels.append(after.name)

        if before.name in discord_config.markov_channels and after.name not in discord_config.markov_channels:
            discord_config.markov_channels.append(after.name)

        common.console_print("Channel #" + before.name + " has changed to #" + after.name, console_prefix)

def start():
    global is_running

    if is_running:
        return

    common.console_print("Discord Client version " + version, console_prefix)
    discord_commands.load_custom_commands(False)

    if discord_config.token == '':
        common.console_print("Token is not present. Cannot connect to Discord.", console_prefix)
        return

    is_running = True
    discord_client.loop.run_until_complete(discord_client.start(discord_config.token))
    is_running = False

def stop():
    global is_running

    if is_running:
        common.console_print("Shutting down client...", console_prefix)
        future = asyncio.run_coroutine_threadsafe(discord_client.close(), discord_client.loop)

    is_running = False
