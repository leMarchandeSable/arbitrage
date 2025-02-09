import os
import pandas as pd
from utils.loaders import load_yaml, load_pandas, save_pandas
from utils.class_mapper import Mapper


class DatabaseManager:
    """
    A class to handle all interactions with the CSV database.
    """
    def __init__(self, path: str):
        self.path = path
        self.data = load_pandas(self.path)

    def _isnan(self, x) -> bool:
        # return True if x is nan
        return x != x

    def add_instance(self, instance: dict):
        self.data = pd.concat([self.data, pd.DataFrame([instance])], ignore_index=True)

    def save_database(self):
        self.data.drop_duplicates(inplace=True)  # Remove duplicates before saving
        save_pandas(self.data, self.path)

    def standardise_team_names(self, sport: str, mapper: Mapper):

        for index, event in self.data.iterrows():
            try:
                home_team_standard = mapper.map_team_name(sport, event["Home Team Unparse"])
                away_team_standard = mapper.map_team_name(sport, event["Away Team Unparse"])

                self.data.at[index, "Home Team Std"] = home_team_standard
                self.data.at[index, "Away Team Std"] = away_team_standard
            except Exception as e:
                raise e
        self.save_database()

    def standardise_dates(self, mapper: Mapper):

        for index, event in self.data.iterrows():
            try:
                bookmaker = event["Bookmaker"]
                date_unparse = event["Date Unparse"]
                scrapping_time = event["scrapping_time"]

                if self._isnan(date_unparse):
                    continue

                date = mapper.map_date_unparse(bookmaker, date_unparse, scrapping_time)
                self.data.at[index, "Date"] = date

            except KeyError as ke:
                print(f"data row {index}: KeyError 'scrapping_time', 'Date Unparse' or 'Bookmaker' not found {list(event.keys())}")
                raise ke
            except Exception as e:
                print(e)
                raise e

        self.save_database()

    def standardise_sports(self, mapper: Mapper):

        for index, event in self.data.iterrows():
            try:
                sport_unparse = event["Sport Unparse"]

                if self._isnan(sport_unparse):
                    continue

                self.data.at[index, "Sport"] = mapper.map_sport_unparse(sport_unparse)

            except KeyError as ke:
                print(f"data row {index}: Key value not found {event.keys()}")
                raise ke
            except Exception as e:
                print(e)
                raise e

        self.save_database()

    def standardise_category(self, mapper: Mapper):

        for index, event in self.data.iterrows():
            try:
                category_unparse = event["Category Unparse"]

                if self._isnan(category_unparse):
                    continue

                self.data.at[index, "Category"] = mapper.map_category_unparse(category_unparse)

            except KeyError as ke:
                print(f"data row {index}: Key value not found {event.keys()}")
                raise ke
            except Exception as e:
                print(e)
                raise e

        self.save_database()


if __name__ == "__main__":
    config = load_yaml("../../config/bookmaker_config.yml")
    sport = "NHL"

    # db = DatabaseManager(config["path"]["database"])
    # mapping = Mapper(config["path"]["mapping"])
    db = DatabaseManager("../../data/database.csv")
    mapper = Mapper("../../data/mapping.yml")

    # mapping.update_mapper(sport, team_names)
    # db.map_team_names(sport, mapper)
    # db.standardise_dates(mapper)
    db.standardise_sports(mapper)
    db.standardise_category(mapper)
