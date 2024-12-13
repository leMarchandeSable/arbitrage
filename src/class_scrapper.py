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
                team_1, team_2 = self._get_teams(event)
                match_time = self._get_match_time(event)
                odds = self._get_odds(event)

                event_data.append({
                    "Team 1": team_1,
                    "Team 2": team_2,
                    "Time": match_time,
                    "Odds Team 1": odds.get("Team 1", "N/A"),
                    "Odds Draw": odds.get("Draw", "N/A"),
                    "Odds Team 2": odds.get("Team 2", "N/A"),
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

    def _get_teams(self, event) -> (str, str):
        """
        Extracts team names from an event. Should be overridden in subclasses.
        """
        raise NotImplementedError("Subclasses must implement `_get_teams`.")

    def _get_match_time(self, event) -> str:
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
    CLASS_NAMES = {
        "event_block": "psel-event",
        "team_name": "psel-opponent__name",
        "match_time": "psel-timer",
        "odds_data": "psel-outcome__data",
    }

    def _get_events(self):
        return self.soup.find_all('psel-event-main', class_='psel-event')

    def _get_teams(self, event) -> (str, str):
        teams = event.find_all('span', class_='psel-opponent__name')
        team_1 = teams[0].text.strip() if len(teams) > 0 else "Unknown"
        team_2 = teams[1].text.strip() if len(teams) > 1 else "Unknown"
        self.debug_log(f"Teams found: {team_1} vs {team_2}")
        return team_1, team_2

    def _get_match_time(self, event) -> str:
        match_time_element = event.find('time', class_='psel-timer')
        match_time = match_time_element.text.strip() if match_time_element else "Unknown"
        self.debug_log(f"Match time found: {match_time}")
        return match_time

    def _get_odds(self, event) -> Dict[str, str]:
        odds_elements = event.find_all('span', class_='psel-outcome__data')
        odds = {
            "Team 1": odds_elements[0].text.strip() if len(odds_elements) > 0 else "N/A",
            "Draw": odds_elements[1].text.strip() if len(odds_elements) > 1 else "N/A",
            "Team 2": odds_elements[2].text.strip() if len(odds_elements) > 2 else "N/A",
        }
        self.debug_log(f"Odds found: {odds}")
        return odds


class BookmakerB(EventScraper):
    """
    Scraper for Bookmaker B with a different HTML structure.
    """

    def _get_events(self):
        return self.soup.find_all('div', class_='event-block')

    def _get_teams(self, event) -> (str, str):
        teams = event.find_all('div', class_='team-name')
        team_1 = teams[0].text.strip() if len(teams) > 0 else "Unknown"
        team_2 = teams[1].text.strip() if len(teams) > 1 else "Unknown"
        self.debug_log(f"Teams found: {team_1} vs {team_2}")
        return team_1, team_2

    def _get_match_time(self, event) -> str:
        match_time_element = event.find('div', class_='event-time')
        match_time = match_time_element.text.strip() if match_time_element else "Unknown"
        self.debug_log(f"Match time found: {match_time}")
        return match_time

    def _get_odds(self, event) -> Dict[str, str]:
        odds_elements = event.find_all('div', class_='odds-value')
        odds = {
            "Team 1": odds_elements[0].text.strip() if len(odds_elements) > 0 else "N/A",
            "Draw": odds_elements[1].text.strip() if len(odds_elements) > 1 else "N/A",
            "Team 2": odds_elements[2].text.strip() if len(odds_elements) > 2 else "N/A",
        }
        self.debug_log(f"Odds found: {odds}")
        return odds


def main():
    """
    Main function to scrape data from ZEbet using Selenium.
    """
    geckodriver_path = "/path/to/geckodriver"  # Replace with your GeckoDriver path
    url = "https://www.zebet.fr"  # Replace with ZEbet's URL

    # Initialize the scraper
    scraper = Zebet(geckodriver_path, url, debug=True)
    extracted_data = scraper.extract_event_data()

    print("\nExtracted Data:")
    for event in extracted_data:
        print(event)


if __name__ == "__main__":
    main()
