import json
import yaml
import pickle
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import logging
import pandas


# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def save_html(path: str, soup: BeautifulSoup):
    """
    Save a BeautifulSoup object to a file using pickle.

    :param path: File path where the BeautifulSoup object will be saved.
    :param soup: BeautifulSoup object to save.
    """
    try:
        with open(path, "wb") as f:
            pickle.dump(soup, f)
        logger.info(f"HTML saved successfully to {path}.")
    except Exception as e:
        logger.error(f"Failed to save HTML to {path}: {e}")
        raise


def load_html(path: str) -> BeautifulSoup:
    """
    Load a BeautifulSoup object from a file.

    :param path: File path where the BeautifulSoup object is stored.
    :return: Loaded BeautifulSoup object.
    """
    try:
        with open(path, "rb") as f:
            soup_obj = pickle.load(f)
        logger.info(f"HTML loaded successfully from {path}.")
        return soup_obj
    except FileNotFoundError:
        logger.error(f"HTML file not found at {path}.")
        raise
    except Exception as e:
        logger.error(f"Failed to load HTML from {path}: {e}")
        raise


def load_text(path: str, strip: bool = False) -> List[str]:
    """
    Load text lines from a file.

    :param path: File path to the text file.
    :param strip: Whether to strip whitespace from each line.
    :return: List of text lines.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if strip:
            lines = [line.strip() for line in lines]
        logger.info(f"Text file loaded successfully from {path}.")
        return lines
    except FileNotFoundError:
        logger.error(f"Text file not found at {path}.")
        raise
    except Exception as e:
        logger.error(f"Failed to load text file from {path}: {e}")
        raise


def save_yaml(data, path):
    """
    Saves the provided data to a YAML file.

    :param data: The data to save (must be serializable to YAML).
    :param path: The path to the YAML file where data will be saved.
    """
    try:
        with open(path, 'w', encoding='utf-8') as file:
            yaml.dump(data, file, default_flow_style=False, allow_unicode=True)
        logger.info(f"Data successfully saved to {path}")
    except Exception as e:
        logger.error(f"An error occurred while saving the YAML file: {e}")


def load_yaml(path: str) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.

    :param path: Path to the YAML configuration file.
    :return: Parsed configuration as a dictionary.
    """
    try:
        with open(path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
        logger.info(f"Yaml loaded successfully from {path}.")
        return config
    except FileNotFoundError:
        logger.error(f"Yaml file not found at {path}.")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML from {path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while loading yaml from {path}: {e}")
        raise


def load_json(file_path: str) -> Dict[str, Any]:
    """
    Load data from a JSON file.

    :param file_path: Path to the JSON file.
    :return: Parsed JSON data as a dictionary.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        logger.info(f"JSON file loaded successfully from {file_path}.")
        return data
    except FileNotFoundError:
        logger.error(f"JSON file not found at {file_path}.")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON file from {file_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while loading JSON from {file_path}: {e}")
        raise


def save_json(file_path: str, data: Dict[str, Any], mode: str = "w"):
    """
    Save data to a JSON file.

    :param file_path: Path to the JSON file.
    :param data: Data to save.
    :param mode: File write mode (default is "w").
    """
    try:
        with open(file_path, mode, encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"JSON file saved successfully to {file_path}.")
    except Exception as e:
        logger.error(f"Failed to save JSON file to {file_path}: {e}")
        raise


def load_pandas(path: str) -> pandas.DataFrame:
    try:
        data = pandas.read_csv(path)
        logger.info(f"DataFrame successfully loaded from '{path}'")
        return data
    except FileNotFoundError:
        logger.error(f"Pandas file not found at '{path}'.")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while loading Pandas from '{path}': {e}")
        raise


def save_pandas(data: pandas.DataFrame, path: str):
    try:
        data.to_csv(path, index=False)
        logger.info(f"Pandas file saved successfully to '{path}'.")
    except Exception as e:
        logger.error(f"Failed to save Pandas file to '{path}': {e}")
        raise
