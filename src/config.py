
class Config:
    """Base configuration class with default settings."""

    # Web scraping user-agent string (to simulate a browser request)
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    FEATURES_PARSER = "html.parser"

    # To emulate webdriver, download at https://github.com/mozilla/geckodriver/releases
    GECKODRIVER_PATH = "src/utils/geckodriver.exe"

    # Timeout settings for requests (to avoid waiting too long)
    TIMEOUT = 10  # Timeout for network requests (seconds)

    # Folder where raw data will be stored
    RAW_DATA_FOLDER = "./data/raw/"
    # Folder where processed data will be stored
    PROCESSED_DATA_FOLDER = "./data/processed/"
    # Log file path (if you want to save logs)
    LOG_FILE_PATH = "./logs/scraping.log"


class Config_schedule(Config):
    # NHL schedule api: URL_BASE/2024-12-15
    URL_BASE = "https://api-web.nhle.com/v1/schedule"

    SCHEDULE_PATH = "data/schedule_nhl.csv"

class Config_ZEBET(Config):
    URL = "https://www.zebet.fr/paris-hockey-sur-glace/nhl"

    CLASS_EVENT = "psel-event" # tag: psel-event-live or psel-event-main
    CLASS_DATE = "psel-timer"
    CLASS_TEAM = "psel-opponent__name"
    CLASS_ODD = "psel-outcome__data"
    CLASS_NO_BET = "psel-bet-suspended" # tag: caption
    # psel-visually-hidden  'Face à Face - Match' or ' 1 N 2 - Temps Réglementaire'
    # tag: button, class="psel-market-filters__label" (selection of bet type 1N2, F2F...)