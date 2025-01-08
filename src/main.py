from netbet import Netbet
from winamax import Winamax
from zebet import Zebet
from utils.loader_csv import DatabaseManager
from utils.loader_config import load_config


# --------------------- CONST ---------------------
config = load_config("config/bookmaker_config.yml")
sport = "NHL"


# Initialize the scraper
scrapers = [
    Winamax(config, sport, debug=False),
    Zebet(config, sport, debug=False),
    Netbet(config, sport, debug=False),
]

extracted_data = []
for scraper in scrapers:
    extracted_data += scraper.extract_event_data()

# database connection
df = DatabaseManager(config["path"]["database"])

for event in extracted_data:
    print(event)
    df.add_instance(event)
df.save_database()
