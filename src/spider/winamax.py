from utils.class_webdriver import WebDriver
from utils.class_logger import Logger
from utils.loaders import load_config, load_json, save_json, load_text


config = load_config("../../config/bookmaker_config.yml")
debug = False
timeout = 90000
mode = "playwright"
url = "https://www.winamax.fr/paris-sportifs"
actions = [

]

logger = Logger("Winamax", debug)

links = load_text("winamax_links.txt", strip=True)
links_404 = []
sports = load_json("winamax_sport.json")


for link in links:

    if link in sports.values():
        continue
    if link in sports["404"]:
        continue

    try:
        # goto
        webdriver = WebDriver(config, logger, mode, debug, timeout)
        soup = webdriver.fetch_html(link, actions=actions)
        # sport name
        sport = soup.find(class_="sc-dYjQgI gzwFMB").text
        print(sport)
        # nb odds
        event = soup.find_all(class_="sc-gmaIPR hSSQYr")[0]
        nb_odds = len(event.find_all(class_="sc-fxLEgV bogQto"))
        print(nb_odds)
        if nb_odds != 3:
            raise "more than 3 odds"

        sports[sport] = link
        del webdriver
    except TimeoutError as te:
        print(te)
    except Exception as e:
        print(e)
        sports["404"].append(link)

    save_json("winamax_sport.json", sports, mode="w")
