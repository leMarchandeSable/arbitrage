import datetime
from bs4 import BeautifulSoup
import os

from utils.class_logger import Logger
from utils.class_webdriver import WebDriver


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
        self.timeout = 120000  # Wait timeout for content to load (ms)
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

    def _get_actions(self) -> list:
        if "actions" in self.config["bookmakers"][self.get_bookmaker_name()].keys():
            return self.config["bookmakers"][self.get_bookmaker_name()]["actions"]

    def extract_event_data(self) -> list:
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
                    "Home Team Unparse": teams["home"],
                    "Away Team Unparse": teams["away"],
                    "Home Odd": odds["home"],
                    "Draw Odd": odds["draw"],
                    "Away Odd": odds["away"],
                    "Date Unparse": date["element"],
                    "scrapping_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                event_data.append(data)
                # self.logger.info_log(f"Processed event {index}: {data}")

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

    def _get_teams(self, event):
        """
        Extracts team names from an event. Should be overridden in subclasses.
        """
        raise NotImplementedError("Subclasses must implement `_get_teams`.")

    def _get_match_time(self, event):
        """
        Extracts match time from an event. Should be overridden in subclasses.
        """
        raise NotImplementedError("Subclasses must implement `_get_match_time`.")

    def _get_odds(self, event):
        """
        Extracts odds from an event. Should be overridden in subclasses.
        """
        raise NotImplementedError("Subclasses must implement `_get_odds`.")

    def get_bookmaker_name(self) -> str:
        return type(self).__name__
