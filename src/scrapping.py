import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By

from config import Config_ZEBET


def get_driver_url(geckodriver_path, url):
    # Set up GeckoDriver service
    service = Service(geckodriver_path)  # Path to your GeckoDriver

    # Set up Firefox options
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")  # Run in headless mode (no GUI)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Launch the Firefox browser
    driver = webdriver.Firefox(service=service, options=options)

    # Navigate to the ZEbet page
    driver.get(url)

    # Extract page source or interact with the page
    html = driver.page_source

    # Quit the driver
    driver.quit()

    return html


conf = Config_ZEBET()

html = get_driver_url(conf.GECKODRIVER_PATH, conf.URL)
# Parse the HTML content
soup = BeautifulSoup(html, features=conf.FEATURES_PARSER)

# Find all events
events = soup.find_all(class_=conf.CLASS_EVENT)

# Extract data for each event
event_data = []
for event in events:
    try:
        # Date and time: 'À 01h30' or 'Demain à 01h00' or 'Le 14/12 à 02h00'
        date_time = event.findNext(class_=conf.CLASS_DATE).text
        print(date_time)
        print(date_time.strip())
        print(date_time.split(' à '))
        date = date_time.split(' à ')[0]
        time = date_time.split(' à ')[1]

        # Teams names: 'CLB BJackets'
        home_name = event.findNext(class_=conf.CLASS_TEAM).text
        home_team_short = home_name.split()[0]
        home_team = home_name.split()[1]

        away_name = event.findNext(class_=conf.CLASS_TEAM).text
        away_team_short = away_name.split()[0]
        away_team = away_name.split()[1]

        # Odds: '3,05' (home, null, away)
        home_odd = float(event.findNext(class_=conf.CLASS_ODD).text.replace(',', '.'))
        null_odd = float(event.findNext(class_=conf.CLASS_ODD).text.replace(',', '.'))
        away_odd = float(event.findNext(class_=conf.CLASS_ODD).text.replace(',', '.'))

        event_data.append({
            "Date": date,
            "Start Time (UTC)": time,
            "Home Team": home_team,
            "Home Team Abbreviation": home_team_short,
            "Away Team": away_team,
            "Away Team Abbreviation": away_team_short,
            "Home Odd": home_odd,
            "Null Odd": null_odd,
            "Away Odd": away_odd,
        })
        # Store the extracted data

    except Exception as e:
        print(f"Error processing event: {e}")


for event in event_data:
    print(event)