from bookmakers.netbet import Netbet
from bookmakers.winamax import Winamax
from bookmakers.zebet import Zebet
from utils.class_databasemanager import DatabaseManager
from utils.loaders import load_config
from utils.class_mapper import Mapper
from utils.function_esperance import find_arbitrage


class App:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = load_config(self.config_path)
        self.db = DatabaseManager(self.config["path"]["database"])
        self.mapping = Mapper(self.config["path"]["mapping"])

    def collect_games(self, sport: str):
        scrapers = [
            Winamax(self.config, sport, debug=False),
            Zebet(self.config, sport, debug=False),
            Netbet(self.config, sport, debug=False),
        ]

        extracted_data = []
        for scraper in scrapers:
            extracted_data += scraper.extract_event_data()

        for event in extracted_data:
            print(event)
            self.db.add_instance(event)
        self.db.save_database()

        self.db.map_team_names(sport, self.mapping)
        find_arbitrage(self.db.data)


if __name__ == "__main__":

    app = App("config/bookmaker_config.yml")
    app.collect_games(sport="NHL")
