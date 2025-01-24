import datetime
from utils.loaders import load_yaml
from utils.class_scrapper import EventScraper
from utils.class_databasemanager import DatabaseManager


class Zebet(EventScraper):
    """
    Scraper for Bookmaker A with specific HTML structure.
    """

    # CSS selectors for class names, grouped for easy maintenance
    CSS = {
        "tag": {
            "event": "psel-event-main",
            "event live": "psel-event-live",
            "date": "time",
            "team": "span",
            "odd": "span",
        },
        "class": {
            "event": "psel-event",
            "event live": "psel-event",
            "date": "psel-timer",
            "team": "psel-opponent__name",
            "odd": "psel-outcome__data",
        }
    }

    def _get_events(self):
        """
        Extracts all events from the page.
        """
        events = self.soup.find_all(self.CSS['tag']['event'], class_=self.CSS['class']['event'])
        if not events:
            self.logger.debug_log("No events found.")
            raise ValueError("No events were found on the page.")
        return events

    def _get_teams(self, event) -> dict:

        teams_element = event.find_all(self.CSS['tag']['team'], class_=self.CSS['class']['team'])
        self.logger.debug_log(f"CSS Bloc teams found: {teams_element}")

        if len(teams_element) != 2:
            raise ValueError(f"More than 2 teams detected {teams_element}")

        teams = {
            "home short": "",
            "home": teams_element[0].text,
            "away short": "",
            "away": teams_element[1].text,
        }

        self.logger.debug_log(f"Teams found: {teams['home']} vs {teams['away']}")
        return teams

    def _get_match_time(self, event) -> str:
        date_time_element = event.find(self.CSS['tag']['date'], class_=self.CSS['class']['date'])
        self.logger.debug_log(f"CSS Bloc time found: {date_time_element}")

        # date_time_element: 'À 02h00', 'Demain à 01H30' or 'Le 18/12 à 01h30'
        return date_time_element.text

    def _get_odds(self, event) -> dict:
        odds_elements = event.find_all(self.CSS['tag']['odd'], class_=self.CSS['class']['odd'])
        self.logger.debug_log(f"CSS Bloc odds found: {odds_elements}")

        if len(odds_elements) != 3:
            self.logger.debug_log(f"Not exactly 3 odds: {odds_elements}")

        odds = {
            "home": float(odds_elements[0].text.replace(',', '.')),
            "draw": float(odds_elements[1].text.replace(',', '.')),
            "away": float(odds_elements[2].text.replace(',', '.')),
        }

        self.logger.debug_log(f"Odds found: {odds}")
        return odds


def main():

    config = load_yaml("../../config/bookmaker_config.yml")
    db = DatabaseManager("../../data/database.csv")
    sport = "football"     # "NHL"

    urls = ['https://www.zebet.fr/paris-football/algerie/d1-algerie', 'https://www.zebet.fr/paris-football/allemagne/bundesliga-1', 'https://www.zebet.fr/paris-football/allemagne/bundesliga-2', 'https://www.zebet.fr/paris-football/allemagne/cpe-allemagne', 'https://www.zebet.fr/paris-football/angleterre/championship', 'https://www.zebet.fr/paris-football/angleterre/efl-cup', 'https://www.zebet.fr/paris-football/angleterre/fa-cup', 'https://www.zebet.fr/paris-football/angleterre/premier-league', 'https://www.zebet.fr/paris-football/arabie-saoudite/d1-arabie-saoudite', 'https://www.zebet.fr/paris-football/argentine/d1-argentine', 'https://www.zebet.fr/paris-football/australie/d1-australie', 'https://www.zebet.fr/paris-football/azerbaidjan/d1-azerbaidjan', 'https://www.zebet.fr/paris-football/belgique/d1-belgique', 'https://www.zebet.fr/paris-football/bulgarie/d1-bulgarie', 'https://www.zebet.fr/paris-football/chypre/d1-chypre', 'https://www.zebet.fr/paris-football/colombie/d1-colombie', 'https://www.zebet.fr/paris-football/coupes-d-europe/championsleague', 'https://www.zebet.fr/paris-football/coupes-d-europe/europa-conference', 'https://www.zebet.fr/paris-football/coupes-d-europe/europa-league', 'https://www.zebet.fr/paris-football/croatie/d1-croatie', 'https://www.zebet.fr/paris-football/danemark/d1-danemark', 'https://www.zebet.fr/paris-football/ecosse/d1-ecosse', 'https://www.zebet.fr/paris-football/espagne/copa-del-rey', 'https://www.zebet.fr/paris-football/espagne/laliga', 'https://www.zebet.fr/paris-football/espagne/laliga-2', 'https://www.zebet.fr/paris-football/france/ligue-1-mcdonalds', 'https://www.zebet.fr/paris-football/france/ligue-2-bkt', 'https://www.zebet.fr/paris-football/grece/d1-grece', 'https://www.zebet.fr/paris-football/international/coupe-du-monde-usa-2026', 'https://www.zebet.fr/paris-football/international/ldn', 'https://www.zebet.fr/paris-football/irlande-du-nord/d1-irlande-nord', 'https://www.zebet.fr/paris-football/israel/d1-israel', 'https://www.zebet.fr/paris-football/italie/coupe-d-italie', 'https://www.zebet.fr/paris-football/italie/serie-a', 'https://www.zebet.fr/paris-football/italie/serie-b', 'https://www.zebet.fr/paris-football/maroc/d1-maroc', 'https://www.zebet.fr/paris-football/mexique/d1-mexique', 'https://www.zebet.fr/paris-football/multibuts/multibuts', 'https://www.zebet.fr/paris-football/paraguay/d1-paraguay', 'https://www.zebet.fr/paris-football/pays-bas/d1-pays-bas', 'https://www.zebet.fr/paris-football/pays-de-galles/d1-p-degalles', 'https://www.zebet.fr/paris-football/pologne/d1-pologne', 'https://www.zebet.fr/paris-football/portugal/d2-portugal', 'https://www.zebet.fr/paris-football/portugal/liga-portugal', 'https://www.zebet.fr/paris-football/roumanie/d1-roumanie', 'https://www.zebet.fr/paris-football/suisse/d1-suisse', 'https://www.zebet.fr/paris-football/turquie/d1-turquie']

    # Initialize the scraper
    scraper = Zebet(config, sport, debug=True)
    extracted_data = scraper.extract_event_data()

    print("\nExtracted Data:")
    for event in extracted_data:
        print(event)
        db.add_instance(event)
    # db.save_database()


if __name__ == "__main__":
    main()
