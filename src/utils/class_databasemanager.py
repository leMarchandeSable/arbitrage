import os
import pandas as pd
from utils.loaders import load_config
from utils.class_mapper import Mapper


class DatabaseManager:
    """
    A class to handle all interactions with the CSV database.
    """
    def __init__(self, path: str):
        self.path = path
        self.data = self._load_database()

    def _load_database(self) -> pd:
        # Check if the CSV file exists
        if os.path.exists(self.path):
            return pd.read_csv(self.path)
        return pd.DataFrame()

    def add_instance(self, instance: dict):
        self.data = pd.concat([self.data, pd.DataFrame([instance])], ignore_index=True)

    def save_database(self):
        self.data.drop_duplicates(inplace=True)  # Remove duplicates before saving
        self.data.to_csv(self.path, index=False)

    def get_data(self):
        return self.data

    def show_data(self):
        print(self.data.head)

    def map_team_names(self, sport: str, mapping: Mapper):

        for index, event in self.data.iterrows():
            try:
                home_team_standard = mapping.map_team_name(sport, event["Home Team Unparse"])
                away_team_standard = mapping.map_team_name(sport, event["Away Team Unparse"])

                self.data.at[index, "Home Team Std"] = home_team_standard
                self.data.at[index, "Away Team Std"] = away_team_standard
            except Exception as e:
                raise e
        self.save_database()


if __name__ == "__main__":
    config = load_config("../../config/bookmaker_config.yml")
    sport = "NHL"

    # db = DatabaseManager(config["path"]["database"])
    # mapping = Mapper(config["path"]["mapping"])
    db = DatabaseManager("../../data/database.csv")
    mapping = Mapper("../../data/mapping.yml")

    team_names = list(db.data["Home Team Unparse"]) + list(db.data["Away Team Unparse"])

    # Rename the existing DataFrame columns (columns={'oldName1': 'newName1', 'oldName2': 'newName2'})
    # db.data.rename(columns={'Home Team': 'Home Team Unparse', 'Away Team': 'Away Team Unparse'}, inplace=True)

    # mapping.update_mapper(sport, team_names)
    db.map_team_names(sport, mapping)
