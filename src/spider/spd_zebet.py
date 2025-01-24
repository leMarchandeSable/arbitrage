from utils.class_webdriver import WebDriver
from utils.class_logger import Logger
from utils.loaders import *
from utils.function_matchs import clean_keys_in_dict


def get_all_links(soup: BeautifulSoup) -> list:
    a_div = soup.find_all("a")

    links = []
    for a in a_div:
        try:
            # example of a["href"]: "/paris-football/coupes-d-europe/europa-league"
            elements = a["href"].split('/')

            if len(elements) != 4:
                continue
            if any(excluded in elements for excluded in ["cotes-boostees", "https:", "paris-en-direct"]):
                continue

            links.append(url + a["href"])
        except Exception:
            pass

    return list(set(links))


def get_organise_links(links: list, excluded_sport: list = None) -> dict:

    if not excluded_sport:
        excluded_sport = []

    organised_links = {}
    for link in links:
        elements = link.split('/')

        sport_name = elements[3].replace('paris-', '')
        category_name = elements[4]
        tournament_name = elements[5]

        if sport_name in excluded_sport:
            continue

        organised_links.setdefault(sport_name, {}).setdefault(category_name, {})[tournament_name] = link
    return organised_links


if __name__ == "__main__":

    config = load_yaml("../../config/bookmaker_config.yml")
    debug = False
    mode = "playwright"
    timeout = 120000
    url = "https://www.zebet.fr"
    actions = [
        {"wait_for_selector": "#popin_tc_privacy_button_2"},
        {"click_on": "#popin_tc_privacy_button_2"},
    ]
    excluded_sport = ['biathlon', 'formule-1', 'golf', 'moto', 'nascar', 'ski-alpin', 'ski-de-fond']

    logger = Logger("Zebet", debug)
    webdriver = WebDriver(config, logger, mode, debug, timeout)
    soup = webdriver.fetch_html(url, actions=actions)

    links = get_all_links(soup)
    organise_links = get_organise_links(links, excluded_sport=excluded_sport)
    save_json("urls_zebet.json", organise_links)