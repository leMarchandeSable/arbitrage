import os

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from bs4 import BeautifulSoup
from typing import List, Dict, Optional


class EventScraper:
    """
    Base class for scraping event data. Subclasses should override specific methods
    to handle the unique structure of each bookmaker's HTML.
    """

    def __init__(self, geckodriver_path: str, url: str, debug: bool = False):
        """
        Initialize the EventScraper with a URL and Selenium configuration.
        :param geckodriver_path: Path to GeckoDriver executable.
        :param url: The URL to fetch HTML content from.
        :param debug: Enable or disable debug logging.
        """
        self.url = url
        self.geckodriver_path = geckodriver_path
        self.debug = debug
        self.soup = self._fetch_html()

    def debug_log(self, message: str):
        """
        Logs debug messages if debugging is enabled.
        :param message: The debug message to log.
        """
        if self.debug:
            print(f"[DEBUG] {message}")

    def _fetch_html(self) -> BeautifulSoup:
        """
        Fetches HTML content from the specified URL using Selenium.
        :return: A BeautifulSoup object of the fetched HTML.
        """
        try:
            self.debug_log(f"Fetching data from {self.url} using Selenium...")
            # Set up Selenium WebDriver
            service = Service(self.geckodriver_path)
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")  # Run in headless mode (no GUI)
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.binary_location = 'C:/Program Files/Mozilla Firefox/firefox.exe'

            driver = webdriver.Firefox(service=service, options=options)
            driver.get(self.url)
            html = driver.page_source
            driver.quit()

            self.debug_log("HTML content fetched successfully.")
            return BeautifulSoup(html, 'html.parser')
        except Exception as e:
            self.debug_log(f"Error fetching HTML content: {e}")
            raise

    def extract_event_data(self) -> List[Dict[str, Optional[str]]]:
        """
        Extracts event data. Calls subclass-specific methods for data extraction.
        :return: A list of dictionaries containing event data.
        """
        events = self._get_events()
        self.debug_log(f"Found {len(events)} events.")
        event_data = []

        for index, event in enumerate(events, start=1):
            try:
                self.debug_log(f"Processing event {index}/{len(events)}...")
                teams = self._get_teams(event)
                date = self._get_match_time(event)
                odds = self._get_odds(event)

                event_data.append({
                    "Date": date['day'],
                    "Start Time (UTC)": date['time'],
                    "Home Team": teams['home'],
                    "Home Team Abbreviation": teams['home short'],
                    "Away Team": teams['away'],
                    "Away Team Abbreviation": teams['away short'],
                    "Home Odd": odds['home'],
                    "Draw Odd": odds['draw'],
                    "Away Odd": odds['away'],
                })

                self.debug_log(f"Event {index} processed successfully: {event_data[-1]}")
            except Exception as e:
                self.debug_log(f"Error processing event {index}: {e}")

        return event_data

    def _get_events(self):
        """
        Finds and returns all event elements. Should be overridden in subclasses.
        """
        raise NotImplementedError("Subclasses must implement `_get_events`.")

    def _get_teams(self, event) -> (str, str, str, str):
        """
        Extracts team names from an event. Should be overridden in subclasses.
        """
        raise NotImplementedError("Subclasses must implement `_get_teams`.")

    def _get_match_time(self, event) -> (str, str):
        """
        Extracts match time from an event. Should be overridden in subclasses.
        """
        raise NotImplementedError("Subclasses must implement `_get_match_time`.")

    def _get_odds(self, event) -> Dict[str, str]:
        """
        Extracts odds from an event. Should be overridden in subclasses.
        """
        raise NotImplementedError("Subclasses must implement `_get_odds`.")


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
        return self.soup.find_all(self.CSS['tag']['event'], class_=self.CSS['class']['event'])

    def _get_teams(self, event) -> Dict[str, str]:
        teams_element = event.find_all(self.CSS['tag']['team'], class_=self.CSS['class']['team'])
        self.debug_log(f"CSS Bloc teams found: {teams_element}")

        if len(teams_element) != 2:
            self.debug_log(f"Not exactly 2 teams: {teams_element}")
            raise

        teams = {
            "home short": teams_element[0].text.split()[0],
            "home": teams_element[0].text.split()[1],
            "away short": teams_element[1].text.split()[0],
            "away": teams_element[1].text.split()[1],
        }

        self.debug_log(f"Teams found: {teams['home short']} {teams['home']} vs {teams['away short']} {teams['away']}")
        return teams

    def _get_match_time(self, event) -> Dict[str, str]:
        date_time_element = event.find(self.CSS['tag']['date'], class_=self.CSS['class']['date'])
        self.debug_log(f"CSS Bloc time found: {date_time_element}")

        day_element = date_time_element.text.split(' à ')[0]
        time_element = date_time_element.text.split(' à ')[1]

        date = {
            "day": day_element,
            "time": time_element,
        }
        self.debug_log(f"Date found: {date['day']} / {date['time']}")
        return date

    def _get_odds(self, event) -> Dict[str, float]:
        odds_elements = event.find_all(self.CSS['tag']['odd'], class_=self.CSS['class']['odd'])
        self.debug_log(f"CSS Bloc odds found: {odds_elements}")

        if len(odds_elements) != 3:
            self.debug_log(f"Not exactly 3 odds: {odds_elements}")
            raise

        odds = {
            "home": float(odds_elements[0].text.replace(',', '.')),
            "draw": float(odds_elements[1].text.replace(',', '.')),
            "away": float(odds_elements[2].text.replace(',', '.')),
        }

        self.debug_log(f"Odds found: {odds}")
        return odds


def main():
    """
    Main function to scrape data from ZEbet using Selenium.
    """
    geckodriver_path = "src/utils/geckodriver.exe"  # Replace with your GeckoDriver path
    url = "https://www.zebet.fr/paris-hockey-sur-glace/nhl"  # Replace with ZEbet's URL

    # Initialize the scraper
    scraper = Zebet(geckodriver_path, url, debug=True)
    extracted_data = scraper.extract_event_data()

    print("\nExtracted Data:")
    for event in extracted_data:
        print(event)


if __name__ == "__main__":
    main()
