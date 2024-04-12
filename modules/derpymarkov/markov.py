from . import config
from . import derpymodel
from . import derpy_common
from . import generator
import importlib
import re
import random
import time
import threading
import markovify
import os
import common
from collections import defaultdict

VERSION = 'v0.9.4'
common.versions.update({'derpymarkov':VERSION})
lines = list()
commands = defaultdict(dict)
unique_words = set()
unique_word_count = 0
line_count = 0
word_count = 0
context_count = 0
console_prefix = "[DerpyMarkov]"
shutting_down = True

def reload():
    importlib.reload(config)

def accepting_input():
    return not shutting_down

def activate(reload):
    """
    Load and initialize everything then get markov running.
    """

    global shutting_down, lines, main_dictionary_file

    shutting_down = False
    derpy_common.doing_chain = False

    if reload:
        reload()

    common.console_print("DerpyMarkov version " + common.versions.get('derpymarkov'), console_prefix)
    common.console_print("Loading main dictionary...", console_prefix)
    input_text = common.text_file_read(config.main_dictionary_file)

    if input_text == '':
        input_text = 'derp'

    derpy_common.model = derpymodel.DerpyText(input_text, state_size = config.state_size)
    lines = generate_lines_from_model(True)
    
    for stat_line in get_statistics(True):
        common.console_print(stat_line, console_prefix)

    common.console_print("Normal reply rate is " + str(config.reply_rate) + " and bot name reply rate is " + str(config.bot_name_reply_rate) + ".", console_prefix)
    common.console_print("The save interval is " + str(config.save_interval) + " seconds.", console_prefix)
    del input_text
    setup_commands()

def get_statistics(formatted):
    """
    Gets a dict of various statistics and returns them.
    
    If formatted is true, return lines of formatted output.
    """

    update_stats()
    stats = {}
    stats['line_count'] = line_count
    stats['word_count'] = word_count
    stats['unique_word_count'] = unique_word_count
    stats['state_size'] = derpy_common.model.state_size
    stats['context_count'] = context_count

    if formatted:
        output = []
        output.append("I know " + str(line_count) + " lines containing a total of " + str(word_count) + " words.")
        output.append(str(unique_word_count) + " of those words are unique.")
        output.append("We are currently using a state size of " + str(derpy_common.model.state_size) + " which generated " + str(context_count) + " contexts.")
        return output

    return stats

def setup_commands():
    global commands

    commands['statistics']['description'] = 'List statistics for markov instance'
    commands['version']['description'] = 'Get current version'

def get_command_list():
    return commands

def incoming_command(command, from_console):
    if not accepting_input():
        return
    
    if from_console and command == 'shutdown':
        shutdown()
        return

    if command == 'statistics':
        stats_output = get_statistics(True)

        if from_console:
            for entry in stats_output:
                common.console_print(entry, console_prefix)
                
        return stats_output

    if command == 'version':
        version_output = "DerpyMarkov version: " + common.versions.get('derpymarkov')
        
        if from_console:
            common.console_print(version_output, console_prefix)

        return version_output
    
    return None

def incoming_message(message, client_name, bot_paged, do_learn):
    """
    The primary input function. At present any content from outside classes or
    modules comes through here. A reply is returned if warranted, otherwise
    returns None.

    message: The content being passed to DerpyMarkov. Should be a string.
    client_name: The current name of the client sending content.
    """

    if not accepting_input():
        return None

    if not isinstance(message, str) or message == "" or message is None:
        return None

    while derpy_common.doing_chain:
        time.sleep(0.05)

    make_reply = False
    reply = None
    split_message = message.split()
    filtered_split = list()
    name_fold = client_name.casefold()

    for index, word in enumerate(split_message):
        word_fold = word.casefold()

        # Check if bot was named in message; if so, remove name and indicate bot was paged
        if word_fold != name_fold and word_fold != "@" + name_fold:
            filtered_split.append(word)
        else:
            bot_paged = True

    prepared_message = prepare_message(" ".join(filtered_split))

    if prepared_message == "":
        return None

    if do_learn:
        learn(prepared_message)

    reply_rand = random.uniform(0, 100.0)

    if bot_paged:
        make_reply = reply_rand <= config.bot_name_reply_rate
    else:
        make_reply = reply_rand <= config.reply_rate

    if make_reply:
        derpy_common.doing_chain = True
        reply = generator.compose_reply(prepared_message)

    derpy_common.doing_chain = False
    return reply

def prepare_message(message):
    """
    Do some filtering on the raw message before sending it to the markov
    chain.
    """
    message = message.replace('"', '')
    split_message = message.split()

    if not config.preserve_message_case:
        for index, substring in enumerate(split_message):
            # Check for case-sensitive things such as URLs and preserve them.
            if config.preserve_special_case:
                if derpy_common.uri_regex.match(substring)\
                or derpy_common.emoticon_regex.match(substring)\
                or derpy_common.hashtag_user_regex.match(substring):
                    continue
            
            split_message[index] = substring.lower() 

    filtered_message = ' '.join(split_message)
    return filtered_message

def learn(text):
    """
    Come here for some edumacation!
    
    text: Content to be learned.
    """

    if not config.learn:
        return

    derpy_common.unsaved = True

    parsed_sentences = list(derpy_common.model.generate_corpus(text))
    lines.extend(list(map(derpy_common.model.word_join, parsed_sentences)))
    new_model = derpymodel.DerpyText(text, state_size = config.state_size)
    derpy_common.model = markovify.combine([ derpy_common.model, new_model ])

def update_stats(parsed_sentences = None):
    global line_count, context_count, word_count, unique_words, unique_word_count

    if parsed_sentences is None:
        word_count = 0
        parsed_sentences = derpy_common.model.parsed_sentences

    for sentence in derpy_common.model.parsed_sentences:
        for word in sentence:
            word_count += 1
            unique_words.add(word)

    line_count = len(lines)
    context_count = len(derpy_common.model.chain.model)
    unique_word_count = len(unique_words)

def generate_lines_from_model(sort):
    lines = list(map(derpy_common.model.word_join, derpy_common.model.parsed_sentences))

    if sort:
        return sorted(lines)
    else:
        return lines

def save():
    """
    Writes the current lines to file. If no changes have been detected since
    last save we don't need to do anything.
    """

    if not derpy_common.unsaved:
        return

    common.console_print("Saving lines...", console_prefix)

    if os.path.exists(config.main_dictionary_file) and not os.path.isfile(config.main_dictionary_file):
        common.console_print("Error! " + config.main_dictionary_filename + " exists but is not a valid file. Cannot save lines.", console_prefix)
        return

    if not os.path.exists(config.main_dictionary_file):
        os.makedirs(config.absolute_dictionary_directory, exist_ok = True)
        common.console_print(config.main_dictionary_filename + " was not found. Creating new file for saving.", console_prefix)

    with threading.Lock():
        with open(config.main_dictionary_file, '+w', encoding = "utf8") as text:
            text.write('\n'.join(sorted(lines)))
            text.close()

    common.console_print("Lines saved!", console_prefix)
    derpy_common.unsaved = False

def shutdown():
    """ 
    Let's do a clean shutdown here.
    """

    shutting_down = True
    save()
    del derpy_common.model
    common.console_print("DerpyMarkov is shutting down now.", console_prefix)
    return True

def timed_loop():
    while not shutting_down:
        if config.save_interval - (time.time() % config.save_interval) < 1:
            save()

        time.sleep(1.0)

timed_loop_thread = threading.Thread(target = timed_loop, args = [])
timed_loop_thread.start()

