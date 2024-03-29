import os
from configparser import ConfigParser

SCRIPT_BASE_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"
CONFIG_PATH = SCRIPT_BASE_PATH + "config/"
CLIENT_CONFIG_PATH = CONFIG_PATH + "clients/"
CONFIG_DEFAULTS_PATH = CONFIG_PATH + "defaults/"
shutting_down = False
markov = None

def console_print(output, prefix = ''):
    if prefix != '':
        prefix = prefix + " "

    print(prefix + output.encode('ascii', 'replace').decode('utf-8', 'ignore'))

def text_file_read(file_location):
    file_input = ''

    if os.path.exists(file_location) and os.path.isfile(file_location):
        with open(file_location, encoding = "utf8", errors = "backslashreplace") as text:
            file_input = text.read()
            text.close()

    return file_input

def load_config_file(config_file, config = None):
    if config is None:
        config = ConfigParser(allow_no_value = True)

    config_text = text_file_read(config_file)
    
    if config_text != '':
        config.read_string(config_text)

    return config

def load_config_from_files(files, config = None):
    if config is None:
        config = ConfigParser(allow_no_value = True)
        
    config.read(files)
    return config