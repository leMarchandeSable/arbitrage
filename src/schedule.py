import requests
import os
import datetime
import pandas as pd

from config import Config_schedule  # Importing the configuration class for API URL and file path


# Fetch JSON data from the API
def get_json_schedule(url):
    """
    Sends a GET request to the specified URL and returns the JSON response.
    Raises an exception if the HTTP status code is not 200.
    """
    r = requests.get(url)
    if r.status_code != 200:
        raise ValueError(f"HTTP Error {r.status_code}: {r.reason}")
    return r.json()


# Extract game details from the JSON response
def get_games(data):
    """
    Processes the JSON data to extract relevant game information.
    Returns a list of dictionaries, each representing a game.
    """
    games_data = []
    for day in data["gameWeek"]:  # Iterate through each game week
        for game in day["games"]:  # Iterate through the games for each day
            games_data.append({
                "Date": day["date"],
                "Away Team": game["awayTeam"]["commonName"]["default"],
                "Away Team Abbreviation": game["awayTeam"]["abbrev"],
                "Home Team": game["homeTeam"]["commonName"]["default"],
                "Home Team Abbreviation": game["homeTeam"]["abbrev"],
                "Venue": game["venue"]["default"],
                "Start Time (UTC)": game["startTimeUTC"],
            })
    return games_data


# Update or create a CSV file with game data
def update_df_games(path, new_games):
    """
    Updates the existing CSV file with new game data or creates a new CSV if it doesn't exist.
    Removes duplicate entries and saves the updated DataFrame to the specified path.
    """
    # Convert the new game data into a DataFrame
    new_games_df = pd.DataFrame(new_games)

    # Check if the file exists and load old data if it does
    if os.path.exists(path):
        old_games_df = pd.read_csv(path)
        # Combine old and new data, removing duplicates
        updated_df = pd.concat([old_games_df, new_games_df]).drop_duplicates()
    else:
        updated_df = new_games_df

    # Save the updated DataFrame to a CSV file
    updated_df.to_csv(path, index=False)


def debug(url, path):
    """
    Debugging function to print the current step, inspect data, and validate operations.
    """
    print("Starting debug...")

    try:
        print(f"Fetching data from URL: {url}")
        data = get_json_schedule(url)
        print(f"Data fetched successfully: {len(data.get('gameWeek', []))} dates found.")

        print("Extracting games...")
        games = get_games(data)
        print(f"Total games extracted: {len(games)}")

        print("Updating the CSV file...")
        update_df_games(path=path, new_games=games)
        print("CSV updated successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    sch = Config_schedule()

    date = datetime.datetime.now().strftime("%Y-%m-%d")
    url = f"{sch.URL_BASE}/{date}/"

    data = get_json_schedule(url)
    games = get_games(data)
    update_df_games(path=sch.SCHEDULE_PATH, new_games=games)


if __name__ == "__main__":
    sch = Config_schedule()  # Load configuration values

    # Get the current date in 'YYYY-MM-DD' format
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    # date = "2024-12-25"
    # Construct the API URL using the base URL and the current date
    url = f"{sch.URL_BASE}/{date}/"

    # Debug the schedule fetching and updating process
    debug(url=url, path=sch.SCHEDULE_PATH)
