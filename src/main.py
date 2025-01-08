from class_scrapper import Zebet, Winamax, Netbet
from utils.csv_loader import DatabaseManager
from utils.config_loader import load_config


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
