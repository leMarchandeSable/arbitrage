from utils.class_webdriver import WebDriver
from utils.class_logger import Logger
from utils.loaders import load_yaml, load_json, save_json, load_text, save_html ,load_html


def get_all_links(soup,  save=True):
    a_div = soup.find_all("a")

    links = []
    for a in a_div:
        try:
            # example of a["href"]: "/paris-football/coupes-d-europe/europa-league"
            elements = a["href"].split('/')

            if len(elements) != 4:
                continue
            if "paris-en-direct" in elements:
                continue
            if "https:" in elements:
                continue

            links.append(url + a["href"])
        except Exception:
            pass

    if save:
        with open("zebet_links.txt", "w") as f:
            for link in links:
                f.write(link + '\n')
    return links


def organise_links(links, save=True):
    sports = {}

    for link in links:
        elements = link.split('/')
        sub_1 = elements[3].replace('paris-', '')
        sub_2 = elements[4]
        sub_3 = elements[5]

        if sub_1 not in sports.keys():
            sports[sub_1] = {}
        if sub_2 not in sports[sub_1].keys():
            sports[sub_1][sub_2] = {}
        if sub_3 not in sports[sub_1][sub_2].keys():
            sports[sub_1][sub_2][sub_3] = link

    if save:
        save_json("zebet_sports.json", sports, mode="w")
    return sports


config = load_yaml("../../config/bookmaker_config.yml")
debug = True
mode = "playwright"
timeout = 120000
local = True
url = "https://www.zebet.fr"
actions = [
    {"wait_for_selector": "#popin_tc_privacy_button_2"},
    {"click_on": "#popin_tc_privacy_button_2"},
]

if local:
    links = load_text("zebet_links.txt", strip=True)
else:
    logger = Logger("Zebet", debug)
    webdriver = WebDriver(config, logger, mode, debug, timeout)
    soup = webdriver.fetch_html(url, actions=actions)
    links = get_all_links(soup, save=True)

sports = organise_links(links, save=True)
