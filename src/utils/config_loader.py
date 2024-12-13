import yaml


def load_config(config_path: str = "config/config.yml") -> dict:
    """
    Loads configuration from a YAML file.
    :param config_path: Path to the YAML configuration file.
    :return: Parsed configuration as a dictionary.
    """
    try:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
            return config
    except FileNotFoundError:
        raise RuntimeError(f"Configuration file not found at {config_path}.")
    except yaml.YAMLError as e:
        raise RuntimeError(f"Error parsing YAML configuration: {e}")
