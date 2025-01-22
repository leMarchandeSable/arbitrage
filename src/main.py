from bookmakers.netbet import Netbet
from bookmakers.winamax import Winamax
from bookmakers.zebet import Zebet
from utils.class_databasemanager import DatabaseManager
from utils.loaders import load_yaml
from utils.class_mapper import Mapper
from utils.function_esperance import find_arbitrage


class App:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = load_yaml(self.config_path)
        self.db = DatabaseManager(self.config["path"]["database"])
        self.mapper = Mapper(self.config["path"]["mapping"])

    def collect_games(self, sport: str):
        scrappers = [
            Winamax(self.config, sport, debug=False),
            Zebet(self.config, sport, debug=False),
            Netbet(self.config, sport, debug=False),
        ]

        extracted_data = []
        for scrapper in scrappers:
            extracted_data += scrapper.extract_event_data()

        for event in extracted_data:
            print(event)
            self.db.add_instance(event)
        self.db.save_database()

        # self.db.standardise_team_names(sport, self.mapper)
        # self.db.standardise_dates(self.mapper)

        # find_arbitrage(self.db.data)


if __name__ == "__main__":

    app = App("config/bookmaker_config.yml")
    app.collect_games(sport="NHL")
