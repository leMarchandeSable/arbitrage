import datetime
from src.utils.loader_config import load_config
from src.utils.class_scrapper import EventScraper


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
            raise

        teams = {
            "home short": "",
            "home": teams_element[0].text,
            "away short": "",
            "away": teams_element[1].text,
        }

        self.logger.debug_log(f"Teams found: {teams['home short']} {teams['home']} vs {teams['away short']} {teams['away']}")
        return teams

    def _parse_date(self, date_time_element: str) -> datetime:
        date = datetime.datetime.now()

        if "À " in date_time_element:
            time_element = date_time_element.replace("À ", "")
        elif "Demain" in date_time_element:
            time_element = date_time_element.replace("Demain à ", "")
            date += datetime.timedelta(days=1)
        else:
            time_element = date_time_element.split(' à ')[1]

            day_element = date_time_element.split(' à ')[0]
            dd, mm = day_element.replace('Le ', '').split('/')
            date = date.replace(month=int(mm))
            date = date.replace(day=int(dd))

        hour, minute = time_element.split('h')
        date = date.replace(hour=int(hour))
        date = date.replace(minute=int(minute))
        date = date.replace(second=0)
        return date

    def _get_match_time(self, event) -> dict:
        date_time_element = event.find(self.CSS['tag']['date'], class_=self.CSS['class']['date'])
        self.logger.debug_log(f"CSS Bloc time found: {date_time_element}")

        # date_time_element: 'À 02h00', 'Demain à 01H30' or 'Le 18/12 à 01h30'
        date_time = self._parse_date(date_time_element.text)

        date = {
            "day": date_time.strftime("%Y-%m-%d"),
            "time": date_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "element": date_time_element.text,
        }
        self.logger.debug_log(f"Date found: {date['time']}")
        return date

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

    config = load_config("../config/bookmaker_config.yml")
    sport = "NHL"     # "NHL"

    # Initialize the scraper
    scraper = Zebet(config, sport, debug=True)
    extracted_data = scraper.extract_event_data()

    print("\nExtracted Data:")
    for event in extracted_data:
        print(event)


if __name__ == "__main__":
    main()
