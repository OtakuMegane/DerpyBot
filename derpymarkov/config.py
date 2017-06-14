from configparser import SafeConfigParser
import pkg_resources
import common

defaults_file = pkg_resources.resource_string(__name__, "config/defaults.ini")
config_file = pkg_resources.resource_string(__name__, "config/config.ini")

config = SafeConfigParser()
config.read_string(defaults_file.decode())
config.read_string(config_file.decode())

text_directory = config.get('General', 'text_directory')
main_text_filename = config.get('General', 'main_text_file')
main_text_file = text_directory + '/' + main_text_filename
supplementary_text_filename = config.get('General', 'supplementary_text_file')
supplementary_text_file = text_directory + '/' + supplementary_text_filename
state_size1 = int(config.get('General', 'state_size'))
learn = common.set_boolean(config.get('General', 'learn'))
save_interval = int(config.get('General', 'save_interval'))

reply_rate = float(config.get('Reply', 'reply_rate'))
bot_name_reply_rate = float(config.get('Reply', 'bot_name_reply_rate'))

sentence_max_words = int(config.get('Sentence', 'sentence_max_words'))
test_output = common.set_boolean(config.get('Sentence', 'test_output'))
use_keywords = common.set_boolean(config.get('Sentence', 'use_keywords'))
try_all_words_for_key = common.set_boolean(config.get('Sentence', 'try_all_words_for_key'))
sentence_with_key_tries = int(config.get('Sentence', 'sentence_with_key_tries'))
max_overlap_ratio = float(config.get('Sentence', 'max_overlap_ratio'))
max_overlap_total = int(config.get('Sentence', 'max_overlap_total'))
random_on_key_fail = common.set_boolean(config.get('Sentence', 'random_on_key_fail'))
