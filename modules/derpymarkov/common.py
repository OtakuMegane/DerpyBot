import os

def set_boolean(config_value):
    if config_value.lower() == "true":
        return True

    if config_value.lower() == "false":
        return False

    return False

def console_print(output, prefix = ''):
    print(prefix + output.encode('ascii', 'replace').decode('utf-8', 'ignore'))

def text_file_read(file_location):
    file_input = ''

    if os.path.exists(file_location) and os.path.isfile(file_location):
        with open(file_location, encoding = "utf8", errors = "backslashreplace") as text:
            file_input = text.read()
            text.close()

    if not file_input:
        file_input = 'derp'

    return file_input
