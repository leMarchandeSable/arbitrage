from utils.class_webdriver import WebDriver
from utils.class_logger import Logger
from utils.loaders import load_config, load_json, save_json, load_text, save_html ,load_html


config = load_config("../../config/bookmaker_config.yml")
debug = True
mode = "playwright"
timeout = 120000
url = "https://www.zebet.fr"
actions = [
    {"click_on": "Continuer sans accepter"},
]

logger = Logger("zebet", debug)
# webdriver = WebDriver(config, logger, mode, debug, timeout)
# soup = webdriver.fetch_html(url, actions=actions)

links = load_text("zebet_links.txt", strip=True)
for link in links:
    print(url + link)

# save_json("winamax_sport.json", sports, mode="w")
