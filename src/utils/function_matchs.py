import re
import unicodedata


def clean_key(key):
    """
    Standardize keys for matching across bookmakers.

    Rules:
    - Convert to lowercase
    - Replace hyphens (-) with spaces
    - Remove extra whitespace
    - Remove non-alphanumeric characters except spaces
    - Normalize accents/diacritics (optional)
    """
    # Lowercase
    key = key.lower()

    # Replace hyphens with spaces
    key = key.replace("-", " ")

    # Normalize accents/diacritics (if needed, uncomment the following lines)
    key = unicodedata.normalize('NFKD', key).encode('ascii', 'ignore').decode('utf-8')

    # Remove non-alphanumeric characters except spaces
    key = re.sub(r"[^a-z0-9\s]", "", key)

    # Remove extra whitespace
    key = " ".join(key.split())

    return key


def clean_keys_in_dict(data):
    """
    Recursively apply key cleaning to all keys in a nested dictionary.
    """
    if isinstance(data, dict):
        cleaned_dict = {}
        for key, value in data.items():
            cleaned_key = clean_key(key)
            cleaned_dict[cleaned_key] = clean_keys_in_dict(value)
        return cleaned_dict
    elif isinstance(data, list):
        return [clean_keys_in_dict(item) for item in data]
    else:
        return data  # Base case: return value if not dict or list
