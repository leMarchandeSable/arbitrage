from utils.class_webdriver import WebDriver
from utils.class_logger import Logger
from utils.loaders import *
from utils.function_matchs import clean_keys_in_dict
import re


def get_preloaded_state(soup: BeautifulSoup) -> dict:

    # Extract the JavaScript object using regex
    match = re.search(r"var PRELOADED_STATE = ({.*?});", str(soup.contents[1]))
    if not match:
        raise ValueError("PRELOADED_STATE not found in the HTML")

    # Parse the JavaScript object into a Python dictionary
    preloaded_state = json.loads(match.group(1))
    return preloaded_state


def get_all_links(soup: BeautifulSoup) -> list:
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
            if any(excluded in elements for excluded in ["match", "paris-en-direct", "account"]):
                continue

            sub_link = a["href"].replace('/paris-sportifs', '')
            links.append(url + sub_link)
        except Exception as e:
            pass

    return list(set(links))


def get_organise_links(links: list, preloaded_state: dict, excluded_sport: list = None) -> dict:

    if not excluded_sport:
        excluded_sport = []

    indexs = {
        "sports": {id: data["sportName"] for id, data in preloaded_state["sports"].items()},
        "categories": {id: data["categoryName"] for id, data in preloaded_state["categories"].items()},
        "tournaments": {id: data["tournamentName"] for id, data in preloaded_state["tournaments"].items()},
    }

    organised_links = {}
    for link in links:
        elements = link.split('sports/')[1].split('/')

        if len(elements) == 3:
            sport_name = indexs["sports"].get(elements[0])
            category_name = indexs["categories"].get(elements[1])
            tournament_name = indexs["tournaments"].get(elements[2])

            if not sport_name or not category_name or not tournament_name:
                continue

            if sport_name in excluded_sport:
                continue

            organised_links.setdefault(sport_name, {}).setdefault(category_name, {})[tournament_name] = link
    return organised_links


if __name__ == "__main__":

    config = load_yaml("../../config/bookmaker_config.yml")
    debug = False
    timeout = 90000
    mode = "playwright"
    url = "https://www.winamax.fr/paris-sportifs"
    actions = config["bookmakers"]["Winamax"]["actions"]
    excluded_sport = ['Automobile', 'Biathlon', 'Cyclisme', 'Formule 1', 'Golf', 'Moto', 'Ski alpin', 'Ski de fond']

    logger = Logger("Winamax", debug)
    webdriver = WebDriver(config, logger, mode, debug, timeout)
    soup = webdriver.fetch_html(url, actions=actions)

    links = get_all_links(soup)
    preloaded_state = get_preloaded_state(soup)
    organise_links = get_organise_links(links, preloaded_state, excluded_sport=excluded_sport)
    save_json("urls_winamax.json", organise_links)
