import yaml

CONFIG = {}



def load_yaml_config(config_file):
    """Load YAML config file

    :param str config_file: The path to the configuration file.

    :returns: A dict of the parsed config file.
    :rtype: dict
    :raises IOError: If the config file cannot be opened.
    """
    if type(config_file) is file:
        content = yaml.load(config_file) or {}
        content['config_path'] = config_file.name
        CONFIG.update(content)
        return CONFIG
    else:
        try:
            with open(config_file, 'r') as f:
                content = yaml.load(f)
                content['config_path'] = config_file
                CONFIG.update(content)
                return CONFIG
        except IOError as e:
            e.message = "Could not open configuration file \"{}\".".format(config_file)
            raise e
