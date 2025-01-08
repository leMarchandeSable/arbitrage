import json


# Load the JSON dictionary
def load_json(file_path: str) -> dict:
    """
    Load NHL team data from a JSON file.
    :param file_path: Path to the JSON file.
    :return: List of dictionaries representing NHL teams.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
