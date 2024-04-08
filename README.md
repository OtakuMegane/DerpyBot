# DerpyBot #

A bot that will train a Markov model from chat messages and generate replies. Originally created because there was no Discord equivalent to the [markovsky-irc bot](https://sourceforge.net/projects/markovsky/). While Markov chat bots do exist for Discord, all that were found at the time this project began used static text sources. None were designed to learn from chat or actively participate.

The name is inspired by the tendency of Markov trained on erratic or lower quality sources such as chat rooms to produce ridiculous output.

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

For reference to what the settings do, check the defaults file for each config.

## Markov ##
When beginning a new dictionary it will take some time before replies can be generated. As the number of learned messages grows you can try increasing the state size to improve results. However this will also increase memory usage and processing time so it may take some experimentation to find the right balance.

The Markov dictionaries are stored in `derpymarkov/dictionaries`. The format used is a plaintext collection of lines which is appended to as the bot learns. While not as efficient at startup as storing the processed markov model it is human readable and editable in case you need to modify the learned content. NOTE: duplicate lines are intentionally stored in the dictionary. This is related to word weight so do not remove duplicate lines unless there's a specific need.

An option to add supplementary dictionaries to the main one is planned for the future.

## Discord ##
It is possible to add simple custom commands for use in the Discord client. At present these are only commands to post content, they can't do any other functions. Commands are defined in the `discord_commands.cfg` found in the main `config` folder. The example file can be used for reference.

## License
DerpyBot  is released under the [MIT License](https://opensource.org/licenses/MIT). This can be viewed in [LICENSE.md](LICENSE.md).