from configparser import ConfigParser
import common
import os

# config.py is just code. Don't put settings here!
# Settings should go in config.cfg

script_location = os.path.dirname(os.path.abspath(__file__))
config = ConfigParser()
common.load_config_file(script_location + '/config/defaults.cfg', config)
common.load_config_file(script_location + '/config/config.cfg', config)

dictionary_directory = config.get('General', 'dictionary_directory', fallback = 'dictionaries')
absolute_dictionary_directory = script_location + '/' + dictionary_directory
main_dictionary_filename = config.get('General', 'main_dictionary_file', fallback = 'main.txt')
main_dictionary_file = absolute_dictionary_directory + '/' + main_dictionary_filename
state_size = config.getint('General', 'state_size', fallback = 1)
learn = config.getboolean('General', 'learn', fallback = True)
save_interval = config.getint('General', 'save_interval', fallback = 900)

reply_rate = config.getfloat('Reply', 'reply_rate', fallback = 2.0)
bot_name_reply_rate = config.getfloat('Reply', 'bot_name_reply_rate', fallback = 100.0)

sentence_max_words = config.getint('Sentence', 'sentence_max_words', fallback = 0)
test_output = config.getboolean('Sentence', 'test_output', fallback = True)
use_keywords = config.getboolean('Sentence', 'use_keywords', fallback = True)
try_all_words_for_key = config.getboolean('Sentence', 'try_all_words_for_key', fallback = True)
sentence_with_key_tries = config.getint('Sentence', 'sentence_with_key_tries', fallback = 50)
max_overlap_ratio = config.getfloat('Sentence', 'max_overlap_ratio', fallback = 0.80)
max_overlap_total = config.getint('Sentence', 'max_overlap_total', fallback = 15)
random_on_key_fail = config.getboolean('Sentence', 'random_on_key_fail', fallback = False)

fix_punctuation = config.getboolean('Post Process', 'fix_punctuation', fallback = True)

preserve_message_case = config.getboolean('Learn', 'preserve_message_case', fallback = False)
preserve_special_case = config.getboolean('Learn', 'preserve_special_case', fallback = True)