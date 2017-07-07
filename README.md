# DerpyBot #

A chat bot with a learning markov-chain module. Originally created because there was no Discord equivalent to the [markovsky-irc bot](https://sourceforge.net/projects/markovsky/). While markov chat bots exist for Discord, all that were found only took manual input at startup and didn't consider words or phrases from the actual chat they were triggered by.

## Requirements ##
 - Python 3.5+ 
 - [markovify](https://github.com/jsvine/markovify)
 - [discord.py](https://github.com/Rapptz/discord.py)
 
## Basic Setup ##
Basic installation is pretty easy. In the main `config` folder, rename `config.cfg.example` to `config.cfg` then adjust settings as needed for your installation. The only settings that must be changed are `owner_id` and `token` as these are necessary for using with Discord. `defaults.cfg` contains documentation on what each of the settings does as well as the default value.

## Markov Setup ##
The derpymarkov module has its own settings. Similar to the basic configuration, go to the `derpymarkov/config` folder and rename `config.cfg.example` to `config.cfg` then change any settings you like. Again 'defaults.cfg' contains documentation for the settings.

The dictionaries are stored in `derpymarkov/dictionaries`. At present the format used is a plaintext collection of lines which is appended to as the bot learns. While not as efficient as storing the processed markov model it is human readable and editable in case you need to correct or clean out certain content. In the case of editing this manually: duplicate lines are intentional. This is related to word weight so there's no need to remove them.

## Discord Commands ##
It is possible to add commands for use in the Discord client. At present these are only commands to post content, they can't do any other functions. Commands are defined in the `custom\_discord\_commands.cfg` found in the config folder. The example file can be used for reference.