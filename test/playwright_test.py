from time import sleep
from playwright.sync_api import Playwright, sync_playwright
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def run(playwright: Playwright, *, url: str) -> dict:
    """This function navigates to a given URL using a browser and returns
    the page's URL and title."""

    # Launch the Chromium browser in non-headless mode (visible UI) to see
    # the browser in action.
    browser = playwright.chromium.launch(headless=False)

    # Open a new browser page.
    page = browser.new_page(viewport={'width': 1600, 'height': 900})

    # Short sleep to be able to see the browser in action.
    sleep(1)

    # Navigate to the specified URL.
    page.goto(url)

    sleep(1)

    # Retrieve the title of the page.
    title = page.title()

    # Close the browser.
    browser.close()

    # Return the page's URL and title as a dictionary.
    return {'url': url, 'title': title}


def main() -> None:
    # Use sync_playwright context manager to close the Playwright instance
    # automatically
    """with sync_playwright() as playwright:
        result = run(playwright, url='https://crawlee.dev')
        print(result)"""

    url = "https://www.winamax.fr/paris-sportifs/live"
    # url = "https://parisportif.pmu.fr/home/wrapper/events?activeSportId=10&leagues=%5B1927%5D"
    url = "https://www.zebet.fr/paris-hockey-sur-glace/nhl"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Use headless=True for headless mode
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(5000)  # Wait for 5 seconds for content to load
        html = page.content()
        browser.close()

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    print(soup.prettify())


if __name__ == '__main__':
    main()
