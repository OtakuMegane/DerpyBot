def set_boolean(config_value):
    if config_value.lower() == "true":
        return True
    
    if config_value.lower() == "false":
        return False
    
    return False