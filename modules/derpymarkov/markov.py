from . import config
from . import derpymodel
import importlib
import re
import random
import time
import threading
import markovify
import os
import common
from collections import defaultdict

version = '0.9.3.8'

model = None
unsaved = False
lines = list()
test_kwargs = {'max_overlap_ratio': config.max_overlap_ratio,
               'max_overlap_total': config.max_overlap_total,
               'test_output': config.test_output}

if config.sentence_max_words > 0:
    test_kwargs['max_words'] = config.sentence_max_words

uri_regex = re.compile("[^\s]*:\/\/[^\s]*")
emoticon_regex = re.compile(":[DPO]|D:|[X|x]D|[Oo][_-][Oo]")
hashtag_user_regex = re.compile("^[@#][^\s]*")

commands = defaultdict(dict)
shutting_down = False
unique_words = set()
unique_word_count = 0
line_count = 0
word_count = 0
context_count = 0
console_prefix = "[DerpyMarkov] "
doing_chain = False

def reload():
    importlib.reload(config)

def accepting_input():
    if not shutting_down:
        return True

    return False

def activate(reload):
    """
    Load and initialize everything then get markov running.
    """

    global model, lines, main_, shutting_down, doing_chain

    shutting_down = False
    doing_chain = False

    if reload:
        reload()

    common.console_print("Loading DerpyMarkov...", console_prefix)
    common.console_print("DerpyMarkov version " + version, console_prefix)
    input_text = common.text_file_read(config.main_dictionary_file)
    model = derpymodel.DerpyText(input_text, state_size = config.state_size1)
    lines = generate_lines_from_model(True)
    get_statistics(True, False)
    common.console_print("Normal reply rate is " + str(config.reply_rate) + " and bot name reply rate is " + str(config.bot_name_reply_rate) + ".", console_prefix)
    del input_text
    setup_commands()

def get_statistics(print_to_console, return_formatted):
    """
    Gets a dict of various statistics and returns them.
    
    print: If True, we print the statistics to console as well.
    """

    update_stats()
    stats = {}
    stats['line_count'] = line_count
    stats['word_count'] = word_count
    stats['unique_word_count'] = unique_word_count
    stats['state_size'] = model.state_size
    stats['context_count'] = context_count

    output = []
    output.append("I know " + str(line_count) + " lines containing a total of " + str(word_count) + " words.")
    output.append(str(unique_word_count) + " of those words are unique.")
    output.append("We are currently using a state size of " + str(model.state_size) + " which generated " + str(context_count) + " contexts.")

    if print_to_console:
        common.console_print(output[0], console_prefix)
        common.console_print(output[1], console_prefix)
        common.console_print(output[2], console_prefix)

    if return_formatted:
        return "\n".join(output)

    return stats

def setup_commands():
    global commands

    commands['statistics']['description'] = 'List statistics for markov instance'
    commands['version']['description'] = 'Get current version'

def get_command_list():
    return commands

def incoming_console_command(command):
    if not accepting_input():
        return

    if command == 'shutdown':
        shutdown()

    if command == 'statistics':
        get_statistics(True, False)

    if command == 'version':
        common.console_print("derpymarkov " + version, console_prefix)

def incoming_message_command(command):
    if not accepting_input():
        return None

    if command == 'statistics':
        stats = get_statistics(False, True)
        return stats

    if command == 'version':
        return "derpymarkov version: " + version

    return None

def incoming_message(message, client_name, do_learn):
    """
    The primary input function. At present any content from outside classes or
    modules comes through here. A reply is returned if warranted, otherwise
    returns None.

    message: The content being passed to DerpyMarkov. Should be a string.
    client_name: The current name of the client sending content.
    """

    global doing_chain

    if not accepting_input():
        return None

    if not isinstance(message, str) or message == "" or message is None:
        return None

    while doing_chain:
        time.sleep(0.05)

    make_reply = False
    bot_named = False
    bot_paged = False
    doing_chain = True
    reply = None
    split_message = message.split()
    name_fold = client_name.casefold()

    for index, word in enumerate(split_message):
        word_fold = word.casefold()
        if index == 0:
            if name_fold in word_fold:
                bot_paged = True

                if len(split_message) > 1:
                    message = message.split(None, 1)[1]
        else:
            if name_fold in word_fold:
                bot_named = True

    prepared_message = prepare_message(message)

    if do_learn:
        learn(prepared_message)

    reply_rand = random.uniform(0, 100.0)

    if bot_named or bot_paged:
        make_reply = reply_rand <= config.bot_name_reply_rate
    else:
        make_reply = reply_rand <= config.reply_rate

    if make_reply:
        reply = compose_reply(prepared_message)

    doing_chain = False
    return reply

def prepare_message(message):
    """
    So some filtering on the raw message before sending it to the markov
    chain.
    """
    message = message.replace('"', '')
    split_message = message.split()

    # Check for case-sensitive things such as URIs and preserve them
    for index, substring in enumerate(split_message):
        if not uri_regex.match(substring)\
        and not emoticon_regex.match(substring)\
        and not hashtag_user_regex.match(substring):
            split_message[index] = substring.lower()

    filtered_message = ' '.join(split_message)
    return filtered_message

def choose_key_phrase(words):
    """
    Used to derive a keyword or phrase from the given text.
    
    words: Input text to be used for key words or phrases.
    """

    wordlist = model.word_split(words)
    index = random.randint(0, len(wordlist))
    key_phrase = wordlist[index - 1]
    return key_phrase

def get_sentence(words, key_phrase):
    """
    We generate sentences here and return them. Starts with the basic
    make_sentence and checks for any keywords (or returns the sentence if
    keywords are disabled). This gives the nicest results but tends to fail
    for words that are uncommon in a dictionary
    
    If the first method fails we attempt making a sentence with a starting
    key word which has a better rate of success but the possible responses
    are more limited and can feel repetitive if everything was done this way.
    
    words: Input text to be used for key words or phrases.
    key_phrase: A specific keyword or phrase can be sent for use instead.
    """

    if config.use_keywords:
        if config.try_all_words_for_key:
            wordlist = model.word_split(words)
            random.shuffle(wordlist)
        else:
            if key_phrase is not None:
                wordlist = key_phrase

    counter = 0
    final_sentence = None
    
    while counter < config.sentence_with_key_tries:
        counter += 1

        try:
            attempt = model.make_sentence(tries = 1, **test_kwargs)
        except KeyError:
            attempt = None

        if attempt is not None:
            if config.use_keywords:
                if final_sentence is None:
                    for word in wordlist:
                        if re.search(r'\b' + re.escape(word) + r'\b', attempt, re.IGNORECASE) is not None:
                            final_sentence = attempt
                            break
            else:
                final_sentence = attempt
                break

    if final_sentence is None:
        try:
            for word in wordlist:
                final_sentence = model.make_sentence_with_start(word, strict = False, **test_kwargs)
                
                if final_sentence is not None:
                    break
        except KeyError:
            final_sentence = None

    if final_sentence is not None:
        final_sentence = clean_up_punctuation(final_sentence)
        
    return final_sentence

def clean_up_punctuation(sentence):
    sentence_fragments = model.word_split(sentence)
    unmatched_open = -1
    unmatched_close = -1
    
    for index, fragment in enumerate(sentence_fragments, start = 1):
        if '(' in fragment:
            unmatched_open = index - 1
        
        if ')' in fragment:
            if unmatched_open is not -1:
                unmatched_open = -1
            else:
                unmatched_close = index - 1

    if unmatched_open is not -1:
        random_index = random.randrange(unmatched_open + 1, len(sentence_fragments))
        sentence_fragments[random_index] = sentence_fragments[random_index] + ')'
        
    if unmatched_close is not -1:
        if unmatched_close < 2:
            sentence_fragments[unmatched_close] = '(' + sentence_fragments[unmatched_close]
        else:
            random_index = random.randrange(0, unmatched_close - 1)
            sentence_fragments[random_index] = sentence_fragments[random_index] + '('
        
    sentence = ' '.join(sentence_fragments)
    return sentence
    
def compose_reply(message):
    key_phrase = None
    sentence = None

    if config.use_keywords:
        key_phrase = choose_key_phrase(message)

    sentence = get_sentence(message, key_phrase)
    reply = sentence

    if reply == message:
        reply = ""

    return reply

def learn(text):
    """
    Come here for some edumacation!
    
    text: Content to be learned.
    """

    global model, unsaved

    if not config.learn:
        return

    unsaved = True

    parsed_sentences = list(model.generate_corpus(text))
    lines.extend(list(map(model.word_join, parsed_sentences)))

    if config.update_stats_on_learn:
        update_stats(parsed_sentences)

    new_model = derpymodel.DerpyText(text, state_size = config.state_size1)
    model = markovify.combine([ model, new_model ])

def update_stats(parsed_sentences = None):
    global line_count, context_count, word_count, unique_words, unique_word_count

    if parsed_sentences is None:
        word_count = 0
        parsed_sentences = model.parsed_sentences

    for sentence in model.parsed_sentences:
        for word in sentence:
            word_count += 1
            unique_words.add(word)

    line_count = len(lines)
    context_count = len(model.chain.model)
    unique_word_count = len(unique_words)

def generate_lines_from_model(sort):
    lines = list(map(model.word_join, model.parsed_sentences))

    if sort:
        return sorted(lines)
    else:
        return lines

def save():
    """
    Writes the current lines to file. If no changes have been detected since
    last save we don't need to do anything.
    """
    global unsaved

    if not unsaved:
        return

    common.console_print("Saving lines...", console_prefix)

    if os.path.exists(config.main_dictionary_file) and not os.path.isfile(config.main_dictionary_file):
        common.console_print("Error! " + config.main_dictionary_filename + " exists but is not a valid file. Cannot save lines.", console_prefix)
        return

    if not os.path.exists(config.main_dictionary_file):
        os.makedirs(config.absolute_dictionary_directory, exist_ok = True)
        common.console_print(config.main_dictionary_filename + " was not found. Creating new file...", console_prefix)

    with threading.Lock():
        with open(config.main_dictionary_file, '+w', encoding = "utf8") as text:
            text.write('\n'.join(sorted(lines)))
            text.close()

    common.console_print("Lines saved!", console_prefix)
    unsaved = False

def shutdown():
    """ 
    Let's do a clean shutdown here.
    """

    global model, shutting_down
    shutting_down = True
    save()
    del model
    common.console_print("DerpyMarkov is shutting down now.", console_prefix)
    return True

def timed_loop():
    while not shutting_down:
        if config.save_interval - (time.time() % config.save_interval) < 1:
            save()

        time.sleep(1.0)

timed_loop_thread = threading.Thread(target = timed_loop, args = [])
timed_loop_thread.start()

