import datetime
import time
import requests
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from playwright.sync_api import Playwright, sync_playwright
from bs4 import BeautifulSoup
from typing import List, Dict, Optional

from src.utils.json_loader import load_json
from src.utils.config_loader import load_config
from src.utils.class_logger import Logger
from src.class_webdriver import WebDriver


class EventScraper:
    """
    Base class for scraping event data. Subclasses should override specific methods
    to handle the unique structure of each bookmaker's HTML.
    """

    def __init__(self, config: dict, sport: str, debug: bool = False):
        """
        Initialize the EventScraper with configuration and sport.

        :param config: Configuration dictionary loaded from YAML or JSON.
        :param sport: The sport to scrape (e.g., "NHL").
        :param debug: Enable or disable debug logging.
        """

        self.config = config
        self.sport = sport
        self.timeout = 5000  # Wait timeout for content to load (ms)
        self.debug = debug
        self.actions = self._get_actions()
        self.mode = self._get_driver_mode()
        self.url = self._get_url()
        self.soup = None
        self.datetime_format = "%Y-%m-%d %H:%M:%S"

        self.logger = Logger(self.get_bookmaker_name(), debug, self.datetime_format)
        self.webdriver = WebDriver(config, self.logger, self.mode, self.debug, self.timeout)

        try:
            self.soup = self.webdriver.fetch_html(self.url, actions=self.actions)
        except Exception as e:
            self.logger.error_log(f"Initialization failed during HTML fetching: {e}")

    def _get_url(self) -> str:
        return self.config["bookmakers"][self.get_bookmaker_name()]["sport"][self.sport]

    def _get_driver_mode(self) -> str:
        return self.config["bookmakers"][self.get_bookmaker_name()]["mode"]

    def _get_actions(self) -> Optional[list]:
        if "actions" in self.config["bookmakers"][self.get_bookmaker_name()].keys():
            return self.config["bookmakers"][self.get_bookmaker_name()]["actions"]

    def extract_event_data(self) -> List[Dict[str, Optional[str]]]:
        """
        Extracts event data by invoking subclass-specific methods.

        :return: event_data, a list of dictionaries containing event data.
        """
        event_data = []

        try:
            events = self._get_events()
            self.logger.info_log(f"Found {len(events)} events.")
        except Exception as e:
            self.logger.error_log(f"Unexpected error while collecting events: {e}")
            return event_data

        for index, event in enumerate(events, start=1):
            try:
                teams = self._get_teams(event)
                date = self._get_match_time(event)
                odds = self._get_odds(event)

                data = {
                    "Bookmaker": self.get_bookmaker_name(),
                    "Sport": self.sport,
                    "Date": date["day"],
                    "Start Time (UTC)": date["time"],
                    "Home Team": teams["home"],
                    "Away Team": teams["away"],
                    "Home Odd": odds["home"],
                    "Draw Odd": odds["draw"],
                    "Away Odd": odds["away"],
                    "Date Unpase": date["element"],
                    "srapping_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                event_data.append(data)
                self.logger.info_log(f"Processed event {index}: {data}")

            except KeyError as key_err:
                self.logger.debug_log(f"Missing key in event {index}: {key_err}")
            except Exception as e:
                self.logger.debug_log(f"Error processing event {index}: {e}")

        return event_data

    def _get_events(self):
        """
        Finds and returns all event elements. Should be overridden in subclasses.
        """
        raise NotImplementedError("Subclasses must implement `_get_events`.")

    def _get_teams(self, event) -> Dict[str, str]:
        """
        Extracts team names from an event. Should be overridden in subclasses.
        """
        raise NotImplementedError("Subclasses must implement `_get_teams`.")

    def _get_match_time(self, event) -> Dict[str, str]:
        """
        Extracts match time from an event. Should be overridden in subclasses.
        """
        raise NotImplementedError("Subclasses must implement `_get_match_time`.")

    def _get_odds(self, event) -> Dict[str, float]:
        """
        Extracts odds from an event. Should be overridden in subclasses.
        """
        raise NotImplementedError("Subclasses must implement `_get_odds`.")

    def get_bookmaker_name(self) -> str:
        return type(self).__name__


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

    def _get_teams(self, event) -> Dict[str, str]:
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

    def _get_match_time(self, event) -> Dict[str, str]:
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

    def _get_odds(self, event) -> Dict[str, float]:
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

    def _get_events(self):
        # from the main page with all the events, we collect the link the all the specific pages
        # specific url game = main url + href url

        # for every url game we fetch url to collect the html (like a normal event)
        # events is a list of html of each event

        events = self.soup.find_all(self.CSS['tag']['event'], class_=self.CSS['class']['event'])
        if not events:
            self.logger.debug_log("No events found.")
            raise ValueError("No events were found on the page.")
        self.logger.info_log(f"Found {len(events)} events.")

        pages = []
        for event in events:
            url_event = "https://www.netbet.fr" + event["href"]
            html = self.webdriver.fetch_html(url_event)
            pages.append(html)

        return pages

    def _get_teams(self, event) -> Dict[str, str]:
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

    def _get_match_time(self, event) -> Dict[str, str]:

        date_time_element = event.find(self.CSS['tag']['date'], class_=self.CSS['class']['date'])
        self.logger.debug_log(f"CSS Bloc time found: {date_time_element}")
        self.logger.debug_log(f"CSS Bloc time found: {date_time_element.text}")

        # date_time_element: 'À 02h00', 'Demain à 01H30' or 'mar. 24 déc. 01:00'
        # date_time = self._parse_date(date_time_element.text)

        date = {
            "day": "",              # datetime.datetime.now().strftime("%Y-%m-%d")
            "time": "",             # date_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "element": date_time_element.text,
        }
        self.logger.debug_log(f"Date found: {date['time']}")
        return date

    def _get_odds(self, event) -> Dict[str, float]:
        odds_elements = event.find_all(self.CSS['tag']['odd'], class_=self.CSS['class']['odd'])
        # self.debug_log(f"CSS Bloc odds found: {odds_elements}")

        odds = {
            "home": float(odds_elements[0].text),
            "draw": float(odds_elements[2].text),
            "away": float(odds_elements[4].text),
        }

        self.logger.debug_log(f"Odds found: {odds}")
        return odds


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

    DATE_FORMAT = {
        "day": ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"],
        "month": ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juill.", "août", "sept.", "oct.", "nov.", "déc."]
    }

    def _get_events(self) -> List[BeautifulSoup]:
        return self.soup.find_all(self.CSS['tag']['event'], class_=self.CSS['class']['event'])

    def _get_teams(self, event) -> Dict[str, str]:
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

        if "Aujourd’hui à " in date_time_element:
            time_element = date_time_element.replace("Aujourd’hui à ", "")
        elif "Demain à " in date_time_element:
            time_element = date_time_element.replace("Demain à ", "")
            date += datetime.timedelta(days=1)
        else:
            time_element = date_time_element.split(' à ')[1]
            day_element = date_time_element.split(' à ')[0]

            # date like: '29 déc. 2024 à 16:45'
            if len(day_element.split()) == 3:
                dd, mm, yyyy = day_element.split()
                month = self.DATE_FORMAT['month'].index(mm) + 1

                date = date.replace(year=int(yyyy))
                date = date.replace(month=month)
                date = date.replace(day=int(dd))

            # date like: 'mardi à 19:35'
            else:
                # delta_day = (weekday_now + weekday_game + 1) % 7
                # exemple:
                #   now=dimanche(6), demain +1, mardi(1)+1 = +2, mecredi(2)+1 = +3
                #   now=jeudi(3), demain +1, samedi(5)+1 = +2, dimanche(6)+1 = +3

                weekday_game = self.DATE_FORMAT['day'].index(day_element)
                weekday_now = date.weekday()
                date += datetime.timedelta(days=(weekday_now + weekday_game + 2) % 7)

        hour, minute = time_element.split(':')
        date = date.replace(hour=int(hour))
        date = date.replace(minute=int(minute))
        date = date.replace(second=0)
        return date

    def _get_match_time(self, event) -> Dict[str, str]:
        date_time_element = event.find(self.CSS['tag']['date'], class_=self.CSS['class']['date'])
        self.logger.debug_log(f"CSS Bloc time found: {date_time_element}")

        # date_time_element: 'Aujourd’hui à 19:35', 'Demain à 01:00', 'mardi à 01:45' or '29 déc. 2024 à 19:00'
        date_time = self._parse_date(date_time_element.text)

        date = {
            "day": date_time.strftime("%Y-%m-%d"),
            "time": date_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "element": date_time_element.text,
        }
        self.logger.debug_log(f"Date found: {date['time']}")
        return date

    def _get_odds(self, event) -> Dict[str, float]:
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


class Pmu(EventScraper):

    # CSS selectors for class names, grouped for easy maintenance
    CSS = {
        "tag": {
            "event": "div",
            "date": "span",
            "team": "span",
            "odd": "span",
        },
        "class": {
            "event": "sb-event-list__event sb-event-list__event--desktop",
            "date": "sb-event-list__event__time",
            "team": "sb-event-list__competitor sb-event-list__competitor--prematch",
            "odd": "sb-event-list__selection__outcome-value ng-star-inserted",
        }
    }

    DATE_FORMAT = {
        "day": ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"],
        "month": ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juill.", "août", "sept.", "oct.", "nov.", "déc."]
    }

    def _get_events(self) -> List[BeautifulSoup]:
        return self.soup.find_all(self.CSS['tag']['event'], class_=self.CSS['class']['event'])

    def _get_teams(self, event) -> Dict[str, str]:
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

        if "Aujourd’hui à " in date_time_element:
            time_element = date_time_element.replace("Aujourd’hui à ", "")
        elif "Demain à " in date_time_element:
            time_element = date_time_element.replace("Demain à ", "")
            date += datetime.timedelta(days=1)
        else:
            time_element = date_time_element.split(' à ')[1]
            day_element = date_time_element.split(' à ')[0]

            # date like: '29 déc. 2024 à 16:45'
            if len(day_element.split()) == 3:
                dd, mm, yyyy = day_element.split()
                month = self.DATE_FORMAT['month'].index(mm) + 1

                date = date.replace(year=int(yyyy))
                date = date.replace(month=month)
                date = date.replace(day=int(dd))

            # date like: 'mardi à 19:35'
            else:
                # delta_day = (weekday_now + weekday_game + 1) % 7
                # exemple:
                #   now=dimanche(6), demain +1, mardi(1)+1 = +2, mecredi(2)+1 = +3
                #   now=jeudi(3), demain +1, samedi(5)+1 = +2, dimanche(6)+1 = +3

                weekday_game = self.DATE_FORMAT['day'].index(day_element)
                weekday_now = date.weekday()
                date += datetime.timedelta(days=(weekday_now + weekday_game + 2) % 7)

        hour, minute = time_element.split(':')
        date = date.replace(hour=int(hour))
        date = date.replace(minute=int(minute))
        date = date.replace(second=0)
        return date

    def _get_match_time(self, event) -> Dict[str, str]:
        date_time_element = event.find(self.CSS['tag']['date'], class_=self.CSS['class']['date'])
        self.logger.debug_log(f"CSS Bloc time found: {date_time_element}")

        # date_time_element: 'Aujourd’hui à 19:35', 'Demain à 01:00', 'mardi à 01:45' or '29 déc. 2024 à 19:00'
        date_time = self._parse_date(date_time_element.text)

        date = {
            "day": date_time.strftime("%Y-%m-%d"),
            "time": date_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "element": date_time_element.text,
        }
        self.logger.debug_log(f"Date found: {date['time']}")
        return date

    def _get_odds(self, event) -> Dict[str, float]:
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
    # scraper = Winamax(config, sport, debug=True)
    # scraper = Zebet(config, sport, debug=True)
    # scraper = Netbet(config, sport, debug=True)
    scraper = Winamax(config, sport, debug=True)
    extracted_data = scraper.extract_event_data()

    print("\nExtracted Data:")
    for event in extracted_data:
        print(event)


if __name__ == "__main__":
    main()
