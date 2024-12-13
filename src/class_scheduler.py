import requests
import os
import datetime
import pandas as pd


class ScheduleFetcher:
    """
    A class to fetch and manage game schedules from the official API.
    """

    def __init__(self, url_base: str, schedule_path: str, debug: bool = False):
        """
        Initialize the ScheduleFetcher with API details and configuration.
        :param url_base: The base URL of the API.
        :param schedule_path: The file path to store the game schedule CSV.
        :param debug: Enable or disable debug logging.
        """
        self.url_base = url_base
        self.schedule_path = schedule_path
        self.debug = debug

    def debug_log(self, message: str):
        """
        Logs debug messages if debugging is enabled.
        :param message: The debug message to log.
        """
        if self.debug:
            print(f"[DEBUG] {message}")

    def fetch_json(self, date: str) -> dict:
        """
        Fetches the game schedule JSON for the specified date.
        :param date: The date in 'YYYY-MM-DD' format.
        :return: The JSON response from the API.
        """
        url = f"{self.url_base}/{date}/"
        self.debug_log(f"Fetching JSON data from URL: {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise an exception for HTTP errors
            self.debug_log("JSON data fetched successfully.")
            return response.json()
        except requests.Timeout:
            self.debug_log("Request timed out.")
            raise RuntimeError(f"Timeout error while fetching data from {url}")
        except requests.RequestException as e:
            self.debug_log(f"Error fetching data: {e}")
            raise RuntimeError(f"HTTP error occurred while fetching data from {url}: {e}")

    def extract_games(self, data: dict) -> list:
        """
        Extracts game details from the JSON response.
        :param data: The JSON response from the API.
        :return: A list of dictionaries, each representing a game.
        """
        self.debug_log("Extracting games from JSON data...")
        games_data = []

        try:
            for day in data.get("gameWeek", []):  # Iterate through each game week
                for game in day.get("games", []):  # Iterate through the games for each day
                    games_data.append({
                        "Date": day.get("date", "Unknown"),
                        "Away Team": game["awayTeam"]["commonName"]["default"],
                        "Away Team Abbreviation": game["awayTeam"]["abbrev"],
                        "Home Team": game["homeTeam"]["commonName"]["default"],
                        "Home Team Abbreviation": game["homeTeam"]["abbrev"],
                        "Venue": game["venue"]["default"],
                        "Start Time (UTC)": game["startTimeUTC"],
                    })

            self.debug_log(f"Extracted {len(games_data)} games.")
            return games_data
        except KeyError as e:
            self.debug_log(f"Missing key in JSON data: {e}")
            raise RuntimeError("Invalid JSON structure: Missing required fields.")
        except Exception as e:
            self.debug_log(f"Error processing JSON data: {e}")
            raise RuntimeError("An error occurred while processing the JSON data.")

    def update_schedule_csv(self, new_games: list):
        """
        Updates or creates a CSV file with the game schedule.
        :param new_games: The list of new game data to update.
        """
        self.debug_log("Updating the schedule CSV file...")
        try:
            new_games_df = pd.DataFrame(new_games)

            # Check if the CSV file exists
            if os.path.exists(self.schedule_path):
                old_games_df = pd.read_csv(self.schedule_path)
                updated_df = pd.concat([old_games_df, new_games_df]).drop_duplicates()
            else:
                updated_df = new_games_df

            updated_df.to_csv(self.schedule_path, index=False)
            self.debug_log(f"Schedule CSV updated successfully at {self.schedule_path}.")
        except pd.errors.EmptyDataError:
            self.debug_log("The CSV file is empty or corrupted. Creating a new file.")
            new_games_df.to_csv(self.schedule_path, index=False)
        except Exception as e:
            self.debug_log(f"Error updating the schedule CSV: {e}")
            raise RuntimeError(f"An error occurred while updating the CSV file: {e}")

    def run(self, date: str):
        """
        Fetches, extracts, and updates the schedule for the specified date.
        :param date: The date in 'YYYY-MM-DD' format.
        """
        try:
            self.debug_log("Starting the schedule fetching process...")
            json_data = self.fetch_json(date)
            games = self.extract_games(json_data)
            self.update_schedule_csv(games)
            self.debug_log("Schedule fetching process completed successfully.")
        except RuntimeError as e:
            self.debug_log(f"Process failed: {e}")


def main():
    """
    Main function to run the ScheduleFetcher for the current date.
    """
    # Configuration for the API and file path
    URL_BASE = "https://api.example.com/schedule"  # Replace with actual API base URL
    SCHEDULE_PATH = "./schedule.csv"  # Path to store the schedule CSV

    # Initialize ScheduleFetcher with configuration and debug mode enabled
    fetcher = ScheduleFetcher(url_base=URL_BASE, schedule_path=SCHEDULE_PATH, debug=True)

    # Get today's date in 'YYYY-MM-DD' format
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Run the fetcher
    fetcher.run(date)


if __name__ == "__main__":
    main()
