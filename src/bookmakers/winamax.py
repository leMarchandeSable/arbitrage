import re

from utils.loaders import *
from utils.class_scraper import EventScraper
from utils.class_databasemanager import DatabaseManager


class Winamax(EventScraper):

    # CSS selectors for class names, grouped for easy maintenance
    CSS = {
        "tag": {
            "event": "div",
            "event live": "",
            "date": "span",
            "team": "span",
            "odd": "span",
        },
        "class": {
            "event": "sc-gmaIPR hSSQYr",
            "event live": "",
            "date": "sc-jNwOwP kIBFoa",
            "team": "sc-kDrquE",
            "odd": "sc-fxLEgV bogQto",
        }
    }

    def _get_events(self, soup) -> list:
        return soup.find_all(self.CSS['tag']['event'], {"data-testid": re.compile(r"match-card")})

    def _get_teams(self, event) -> dict:
        teams_element = event.find_all(self.CSS['tag']['team'], class_=self.CSS['class']['team'])
        self.logger.debug_log(f"CSS Bloc teams found: {teams_element}")

        if len(teams_element) != 2:
            raise

        teams = {
            "home short": "",
            "home": teams_element[0].text,
            "away short": "",
            "away": teams_element[1].text,
        }

        self.logger.debug_log(f"Teams found: {teams['home short']} {teams['home']} vs {teams['away short']} {teams['away']}")
        return teams

    def _get_match_time(self, event) -> dict:
        date_time_element = event.find(self.CSS['tag']['date'], class_=self.CSS['class']['date'])
        self.logger.debug_log(f"CSS Bloc time found: {date_time_element}")

        # date_time_element: 'Aujourd’hui à 19:35', 'Demain à 01:00', 'mardi à 01:45' or '29 déc. 2024 à 19:00'
        return date_time_element.text

    def _get_odds(self, event) -> dict:
        odds_elements = event.find_all(self.CSS['tag']['odd'], class_=self.CSS['class']['odd'])
        self.logger.debug_log(f"CSS Bloc odds found: {odds_elements}")

        if len(odds_elements) == 3:
            odds = {
                "home": float(odds_elements[0].text.replace(',', '.')),
                "draw": float(odds_elements[1].text.replace(',', '.')),
                "away": float(odds_elements[2].text.replace(',', '.')),
            }
        elif len(odds_elements) == 2:
            odds = {
                "home": float(odds_elements[0].text.replace(',', '.')),
                "draw": "",
                "away": float(odds_elements[1].text.replace(',', '.')),
            }
        else:
            self.logger.debug_log(f"Not exactly 3 odds: {odds_elements}")
            raise ValueError(f"Not exactly 3 odds:\n {odds_elements}")

        self.logger.debug_log(f"Odds found: {odds}")
        return odds


def main():

    config = load_yaml("../../config/bookmaker_config.yml")
    db = DatabaseManager("../../data/database.csv")
    dict_urls = load_json("../spider/urls_winamax.json")

    # Initialize the scraper
    scraper = Winamax(config, debug=False)

    for sport_name in dict_urls.keys():
        for category_name in dict_urls[sport_name].keys():
            for tournament_name in dict_urls[sport_name][category_name].keys():

                keys = {
                    "sport": sport_name,
                    "category": category_name,
                    "tournament": tournament_name,
                }
                url = dict_urls[sport_name][category_name][tournament_name]

                extracted_data = scraper.extract_event_data(keys, url)

                print("\nExtracted Data:")
                for event in extracted_data:
                    print(event)
                    db.add_instance(event)
                db.save_database()


if __name__ == "__main__":
    main()
