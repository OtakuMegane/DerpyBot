import discord
import re

def clean_mentions(text, discord_client):
    possible_mentions = re.search(r'<@[!]?([0-9]*?)>', text)

    if possible_mentions is not None:
        for id in possible_mentions.groups():
            user = discord_client.get_user(int(id))
        
            if user is not None:
                text = re.sub(r'<@[!]?' + id + '>', '@' + user.name, text)
                
    return discord.utils.escape_mentions(text)
