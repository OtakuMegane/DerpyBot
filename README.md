# DerpyBot #

A bot that will train a Markov model from chat messages and generate replies. Originally created because there was no Discord equivalent to the [markovsky-irc bot](https://sourceforge.net/projects/markovsky/). While Markov chat bots do exist for Discord, all that were found at the time this project began used static text sources. None were designed to learn from chat or directly participate.

The name is inspired by the tendency of Markov trained on erratic and lower quality sources such as a chat room to produce strange replies or word salad.

## Requirements ##
General:
 - Python 3.8+ 
 - [markovify](https://github.com/jsvine/markovify) 0.9.4+
 
 To use the Discord client:
 - [discord.py 2.0+](https://github.com/Rapptz/discord.py)
 
## General Setup ##
1. In the main `config` folder rename `derpybot.cfg.example` to `derpybot.cfg` then adjust settings as needed.
2. To enable the Discord client:
 - Rename `discord.cfg.example` to `discord.cfg` then adjust settings as needed.
 - Optionally rename `discord_commands.cfg.example` to `discord_commands.cfg` to enable custom commands.
3. In the DerpyMarkov `config` folder rename `config.cfg.example` to `config.cfg`. Optionally change settings as desired.

For reference to what each setting does, check the defaults file for each config.

## Markov Info ##
The Markov dictionaries are stored in `derpymarkov/dictionaries`. At present the format used is a plaintext collection of lines which is appended to as the bot learns. While not as efficient at startup as storing the processed markov model it is human readable and editable in case you need to add, modify or remove content. NOTE: duplicate lines are intentional. This is related to word weight so there's no need to remove them soley because they are duplicates.

## Discord Commands ##
It is possible to add simple custom commands for use in the Discord client. At present these are only commands to post content, they can't do any other functions. Commands are defined in the `discord_commands.cfg` found in the main `config` folder. The example file can be used for reference.

## License
DerpyBot  is released under the [MIT License](https://opensource.org/licenses/MIT). This can be viewed in [LICENSE.md](LICENSE.md).