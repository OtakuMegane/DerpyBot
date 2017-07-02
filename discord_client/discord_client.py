import asyncio
import discord
import threading
import time
from configparser import SafeConfigParser
import importlib
from . import discord_commands

config = SafeConfigParser()
config.read("config/defaults.ini")
config.read("config/config.ini")

discord_bot_token = config.get('Discord', 'token')
discord_playing = config.get('Discord', 'playing')
discord_client = discord.Client()
discord_channels = []
discord_learn_channels = []

for channel in config.get('Discord', 'channels').split(','):
    discord_channels.append(channel.strip())

for channel in config.get('Discord', 'learn-channels').split(','):
    discord_learn_channels.append(channel.strip())
    
ready = False
markov = None

def console_print(output):
    print("[Discord] " + output)

def logged_in():
    return discord_client.is_logged_in

def still_running(print):
    if print:
        print("[Discord] Client still running! Logged in? " + logged_in())
    return True

@discord_client.event
async def on_ready():
    global ready

    console_print(" We have logged in to Discord!")
    console_print("  Name: " + discord_client.user.name)
    console_print("  ID: " + discord_client.user.id)

    try:
        await discord_client.change_presence(game = discord.Game(name = discord_playing))
        console_print("  Playing: " + discord_playing)
    except:
        console_print("  Could not set 'Playing' status for some reason.")
        console_print(" ")

    ready = True

@discord_client.event
async def on_message(message):
    reply = None
    markov_learn = True

    if message.channel.name not in discord_channels:
        return

    if message.author.bot or message.author == discord_client.user:
        return

    if message.content is "" or message.content is None:
        return

    if message.channel.name not in discord_learn_channels:
        markov_learn = False

    if message.channel.is_private:
        console_print("Direct Message from " + str(message.author) + ": " + str(message.clean_content))
    else:
        console_print("Message from #" + message.channel.name + ": " + str(message.clean_content))

    split_content = message.clean_content.split()
    command_check = split_content.pop(0)

    if '!derpy' in command_check:
        reply = discord_commands.get_commands(message, split_content)
    else:
        if markov is not None:
            reply = markov.incoming_message(message.clean_content, discord_client.user.name, markov_learn)

    if reply is not "" and reply is not None:
        if message.channel.is_private:
            console_print("Direct Message to " + str(message.author) + ": " + str(reply))
        else:
            console_print("Message to #" + message.channel.name + ": " + str(reply))

        if isinstance(reply, str):
            await discord_client.send_message(message.channel, reply)
        else:
            await discord_client.send_message(message.channel, embed = reply)

def launch(markov_instance):
    global markov

    markov = markov_instance
    discord_commands.pass_data(markov, config)  # We'll probably do something better eventually
    discord_commands.load_custom_commands(False)

    try:
        discord_client.loop.run_until_complete(discord_client.start(discord_bot_token))
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
        console_print("Logging out...")

        while logged_in():
            time.sleep(0.25)

    console_print("We are logged out now!")

def shutdown():
    logout()
    console_print("Shutting down client...")
