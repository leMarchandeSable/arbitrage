import datetime
from utils.loaders import *
from utils.class_scraper import EventScraper
from utils.class_databasemanager import DatabaseManager


class Netbet(EventScraper):
    """
    Scraper for Bookmaker A with specific HTML structure.
    """

    # CSS selectors for class names, grouped for easy maintenance
    CSS = {
        "tag": {
            "event": "a",
            "date": "div",
            "team": "div",
            "odd": "span",
        },
        "class": {
            "event": "snc-link-to-event",
            "date": "date-event",
            "team": "container-vertical",
            "odd": "container-odd-and-trend",
        }
    }

    def _get_events(self, soup):
        # from the main page with all the events, we collect the link the all the specific pages
        # specific url game = main url + href url

        # for every url game we fetch url to collect the html (like a normal event)
        # events is a list of html of each event

        events = soup.find_all(self.CSS['tag']['event'], class_=self.CSS['class']['event'])
        if not events:
            self.logger.debug_log("No events found.")
            raise ValueError("No events were found on the page.")
        self.logger.info_log(f"Found {len(events)} events.")

        pages = []
        for event in events:
            url_event = "https://www.netbet.fr" + event["href"]
            html = self.webdriver.fetch_html(url_event, actions=[{"screen_shot": "screen_shot/netbet_"}])
            pages.append(html)

        return pages

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

        # date_time_element: 'LIVE dans 25 min' 'mar. 24 déc. 02:00'
        return date_time_element.text

    def _get_odds(self, event) -> dict:
        # odds_elements = event.find_all(self.CSS['tag']['odd'], class_=self.CSS['class']['odd'])
        # self.debug_log(f"CSS Bloc odds found: {odds_elements}")

        # Find all the containers of betting type 'avec handicape, sans ...'
        all_bets = event.find_all("div", class_="parent-container-event open")
        classic_bet = all_bets[0]         # classic bet is 1N2
        odds_spans = classic_bet.find_all("span", class_="container-odd-and-trend")

        if classic_bet.find("div", class_="over-3"):
            odds = {
                "home": float(odds_spans[0].get_text(strip=True)),
                "draw": float(odds_spans[2].get_text(strip=True)),
                "away": float(odds_spans[4].get_text(strip=True)),
            }
        elif classic_bet.find("div", class_="over-2"):
            odds = {
                "home": float(odds_spans[0].get_text(strip=True)),
                "draw": "",
                "away": float(odds_spans[2].get_text(strip=True)),
            }
        else:
            raise ValueError(f"Not exactly 3 odds")

        self.logger.debug_log(f"Odds found: {odds}")
        return odds


def main():

    config = load_yaml("../../config/bookmaker_config.yml")
    db = DatabaseManager("../../data/database.csv")
    dict_urls = load_json("../spider/urls_netbet.json")

    # Initialize the scraper
    scraper = Netbet(config, debug=False)

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
