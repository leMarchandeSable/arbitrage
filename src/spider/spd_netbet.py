from utils.class_webdriver import WebDriver
from utils.class_logger import Logger
from utils.function_matchs import clean_keys_in_dict
from utils.loaders import *


def fetch_multi_soup(webdriver: WebDriver, url: str, actions: list, url_exentions: list,):

    multi_soup = ""
    for extention in url_exentions:

        soup = webdriver.fetch_html(url + '/' + extention, actions=actions)
        multi_soup += str(soup.contents[1])
    multi_soup = BeautifulSoup(multi_soup, "html.parser")

    return multi_soup


def get_all_links(soup: BeautifulSoup):
    a_div = soup.find_all("a")

    links = []
    for a in a_div:
        try:
            # example of a["href"]: "/paris-sportifs/sports/1/34/144"
            elements = a["href"].split('/')

            if len(elements) < 3:
                continue
            if any(excluded in elements for excluded in ["evenement", "live", "https:", "http:", "promotions"]):
                continue

            links.append(url + a["href"])
        except Exception as e:
            pass

    # make link unique
    return list(set(links))


def get_organise_links(links: list, excluded_sport: list = None) -> dict:

    if not excluded_sport:
        excluded_sport = []

    organised_links = {}
    for link in links:
        elements = link.split('https://www.netbet.fr/')[1].split('/')

        if len(elements) == 3:
            sport_name = elements[0]
            category_name = elements[1]
            tournament_name = elements[2]

            if sport_name in excluded_sport:
                continue

            organised_links.setdefault(sport_name, {}).setdefault(category_name, {})[tournament_name] = link
    return organised_links


if __name__ == "__main__":

    config = load_yaml("../../config/bookmaker_config.yml")
    debug = False
    timeout = 90000
    mode = "playwright"
    url = "https://www.netbet.fr"
    sport_list = ['football', 'tennis', 'basketball', 'foot-us', 'badminton', 'baseball', 'boxe', 'handball', 'hockey-glace', 'mma', 'rugby-a-xiii', 'rugby', 'volleyball']
    # excluded_sport = ['biathlon', 'cyclisme', 'formule 1', 'golf', 'moto', 'ski alpin', 'sport automobile']

    actions = [
        {"wait_for_selector": "button[data-tid='banner-accept']"},
        {"click_on": "button[data-tid='banner-accept']"},
    ]

    logger = Logger("Netbet", debug)
    webdriver = WebDriver(config, logger, mode, debug, timeout)
    soup = fetch_multi_soup(webdriver, url, actions, sport_list)

    links = get_all_links(soup)
    organise_links = get_organise_links(links)
    save_json("urls_netbet.json", organise_links)
