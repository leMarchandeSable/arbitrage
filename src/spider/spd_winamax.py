from utils.class_webdriver import WebDriver
from utils.class_logger import Logger
from utils.loaders import *
import re


def get_preloaded_state(soup, save=True):

    # Extract the JavaScript object using regex
    match = re.search(r"var PRELOADED_STATE = ({.*?});", str(soup.contents[2]))
    if not match:
        raise ValueError("PRELOADED_STATE not found in the HTML")

    # Parse the JavaScript object into a Python dictionary
    preloaded_state = json.loads(match.group(1))
    if save:
        save_json("winamax_preloaded_state.json", preloaded_state)
    return preloaded_state


def get_all_links(soup, save=True):
    a_div = soup.find_all("a")

    links = []
    for a in a_div:
        try:
            # example of a["href"]: "/paris-sportifs/sports/1/34/144"
            elements = a["href"].split('/')

            if len(elements) <= 3:
                continue
            if "paris-sportifs" not in elements:
                continue
            if "match" in elements:
                continue
            if "paris-en-direct" in elements:
                continue
            if "account" in elements:
                continue

            sub_link = a["href"].replace('/paris-sportifs', '')
            links.append(url + sub_link)
        except Exception as e:
            pass

    if save:
        with open("winamax_links.txt", "w") as f:
            for link in links:
                f.write(link + '\n')
    return links


def organise_links(links, preloaded_state, save=True):

    print(preloaded_state.keys())
    indexs = {
        "sports": {id: data["sportName"] for id, data in preloaded_state["sports"].items()},
        "categories": {id: data["categoryName"] for id, data in preloaded_state["categories"].items()},
        "tournaments": {id: data["tournamentName"] for id, data in preloaded_state["tournaments"].items()},
    }

    sports = {}
    for link in links:
        elements = link.split('sports/')[1].split('/')
        sport_name = indexs["sports"][elements[0]]

        if len(elements) == 1:
            sports[sport_name] = {"all": link}
        elif len(elements) == 3:
            category_name = indexs["categories"][elements[1]]
            tournament_name = indexs["tournaments"][elements[2]]

            if sport_name not in sports.keys():
                sports[sport_name] = {}
            if category_name not in sports[sport_name].keys():
                sports[sport_name][category_name] = {}
            sports[sport_name][category_name][tournament_name] = link

    if save:
        save_json("winamax_sports.json", sports)
    return sports


config = load_yaml("../../config/bookmaker_config.yml")
debug = True
timeout = 90000
local = False
mode = "playwright"
url = "https://www.winamax.fr/paris-sportifs"
actions = config["bookmakers"]["Winamax"]["actions"]

if local:
    links = load_text("winamax_links.txt", strip=True)
    preloaded_state = load_json("winamax_preloaded_state.json")
else:
    logger = Logger("Winamax", debug)
    webdriver = WebDriver(config, logger, mode, debug, timeout)
    # soup = webdriver.fetch_html(url, actions=actions)
    soup = load_html("winamax.html")
    links = get_all_links(soup, save=True)
    preloaded_state = get_preloaded_state(soup, save=True)

organise_links(links, preloaded_state, save=True)
