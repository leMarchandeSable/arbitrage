import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from playwright.sync_api import sync_playwright
import playwright._impl._errors as playwright_error
from utils.class_logger import Logger
from utils.loaders import save_html


class WebDriver:
    """
    A class to handle web scraping using Selenium and Playwright.
    """

    def __init__(self, config, logger, mode="playwright", debug=False, timeout=5000):
        """
        Initializes the WebDriver.

        :param config: Configuration dictionary for paths and settings.
        :param mode: The mode of operation ('selenium' or 'playwright').
        :param debug: Whether to enable debug logging and headless mode.
        :param timeout: Timeout in milliseconds for page interactions.
        """

        self.config = config
        self.logger = logger
        self.mode = mode
        self.debug = debug
        self.timeout = timeout

    def fetch_html(self, url: str, actions: list = None) -> BeautifulSoup:
        """
        Fetches HTML content from a URL using the specified mode.

        :param url: The URL to fetch content from.
        :param actions: Optional list of actions to perform on the page.
        :return: A BeautifulSoup object of the fetched HTML.
        :raises ValueError: If HTML content is empty.
        """
        try:
            self.logger.info_log(f"Fetching data from {url} using {self.mode}...")
            start_time = time.time()

            if self.mode == "selenium":
                html = self._fetch_with_selenium(url)
            elif self.mode == "playwright":
                html = self._fetch_with_playwright(url, actions)
            else:
                raise ValueError(f"Unsupported mode: {self.mode}")

            if not html:
                raise ValueError("HTML content is empty.")

            self.logger.info_log(f"HTML fetched successfully in {time.time() - start_time:.2f} seconds.")
            return BeautifulSoup(html, "html.parser")

        except playwright_error.TimeoutError as te:
            self.logger.debug_log(f"Timeout error fetching HTML: {te}")
            raise TimeoutError(f"Timeout error fetching HTML: {te}")
        except Exception as e:
            self.logger.debug_log(f"Error fetching HTML: {e}")
            raise

    def _fetch_with_selenium(self, url: str) -> str:
        """
        Fetches HTML content using Selenium.

        :param url: The URL to fetch content from.
        :return: The HTML content as a string.
        :raises Exception: For any Selenium-related errors.
        """
        try:
            service = Service(self.config["path"]["geckodriver"])
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")
            options.binary_location = self.config["path"]["firefox"]

            driver = webdriver.Firefox(service=service, options=options)
            driver.get(url)
            html = driver.page_source
            driver.quit()
            return html
        except Exception as e:
            self.logger.debug_log(f"Selenium error: {e}")
            raise

    def _fetch_with_playwright(self, url: str, actions: list) -> str:
        """
        Fetches HTML content using Playwright.

        :param url: The URL to fetch content from.
        :param actions: Optional list of actions to perform on the page.
        :return: The HTML content as a string.
        :raises Exception: For any Playwright-related errors.
        """
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=not self.debug, args=["--no-sandbox"])
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                    viewport={"width": 800, "height": 500},
                    locale="fr-FR",
                    timezone_id="Europe/Paris",
                )
                page = context.new_page()
                page.goto(url, timeout=self.timeout)

                if actions:
                    self._perform_actions(page, actions)

                html = page.content()
                return html
            except Exception as e:
                self.logger.debug_log(f"Playwright error: {e}")
                raise
            finally:
                page.close()
                context.close()
                browser.close()

    def _perform_actions(self, page, actions: list):
        """
        Performs a sequence of actions on the page.

        :param page: The Playwright page object.
        :param actions: List of dictionaries specifying actions to perform.
        :raises KeyError: If an action dictionary is missing required keys.
        :raises ValueError: If an unknown action type is encountered.
        """
        for index, action in enumerate(actions, start=1):
            try:
                if "click_on" in action:
                    self.logger.debug_log(f"Action {index}: Clicking on '{action['click_on']}'")
                    # page.click(f"text={action['click_on']}")
                    page.click(action['click_on'])
                elif "click_mouse" in action:
                    self.logger.debug_log(f"Action {index}: Mouse Clicking at '{action['click_mouse']}'")
                    page.mouse.click(*action["click_mouse"])
                elif "wait_for_selector" in action:
                    self.logger.debug_log(f"Action {index}: Waiting for selector '{action['wait_for_selector']}'")
                    page.wait_for_selector(action["wait_for_selector"])
                elif "reload" in action:
                    self.logger.debug_log(f"Action {index}: Reloading the page")
                    page.reload()
                elif "scroll_down" in action:
                    self.logger.debug_log(f"Action {index}: scroll to the bottom of the page")
                    scroll_to_bottom(page, delay=action["scroll_down"])
                elif "screen_shot" in action:
                    self.logger.debug_log(f"Action {index}: take a screen shot of the page")
                    page.screenshot(path=f"{action['screen_shot']}{time.time()}.png", full_page=True)
                else:
                    raise ValueError(f"Unknown action type in action {index}: {action}")
                page.wait_for_timeout(2000)
            except KeyError as e:
                self.logger.debug_log(f"KeyError in action {index}: {e}")
                raise
            except Exception as e:
                self.logger.debug_log(f"Error in action {index}: {e}")
                raise
        page.wait_for_timeout(2000)


def scroll_to_bottom(page, scroll_step=300, delay=0.1):
    """
    Scrolls to the bottom of the page.

    :param page: Playwright page object.
    :param scroll_step: Number of pixels to scroll per step. Default is 300.
    :param delay: Delay in seconds between scroll steps. Default is 0.1 seconds.
    """
    # print("Scrolling to the bottom of the page...")
    save_html("scroll_down.html", page.content())
    previous_height = page.evaluate("document.body.scrollHeight")

    while True:
        # Scroll by the step size
        page.evaluate(f"window.scrollBy(0, {previous_height})")
        time.sleep(delay)  # Wait for the page to load new content

        # Get the new scroll height
        new_height = page.evaluate("document.body.scrollHeight")
        print(previous_height, new_height)
        if new_height == previous_height:
            # print("Reached the bottom of the page.")
            break

        previous_height = new_height
