import datetime
from utils.loaders import load_yaml
from utils.class_scrapper import EventScraper


class Pmu(EventScraper):

    # CSS selectors for class names, grouped for easy maintenance
    CSS = {
        "tag": {
            "event": "div",
            "date": "span",
            "team": "span",
            "odd": "span",
        },
        "class": {
            "event": "sb-event-list__event sb-event-list__event--desktop",
            "date": "sb-event-list__event__time",
            "team": "sb-event-list__competitor sb-event-list__competitor--prematch",
            "odd": "sb-event-list__selection__outcome-value ng-star-inserted",
        }
    }

    DATE_FORMAT = {
        "day": ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"],
        "month": ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juill.", "août", "sept.", "oct.", "nov.", "déc."]
    }

    def _get_events(self) -> list:
        return self.soup.find_all(self.CSS['tag']['event'], class_=self.CSS['class']['event'])

    def _get_teams(self, event) -> dict:
        teams_element = event.find_all(self.CSS['tag']['team'], class_=self.CSS['class']['team'])
        self.logger.debug_log(f"CSS Bloc teams found: {teams_element}")

        if len(teams_element) != 2:
            raise

        teams = {
            "home short": "",
            "home": teams_element[0].text,
            "away short": "",
            "away": teams_element[1].text,
        }

        self.logger.debug_log(f"Teams found: {teams['home short']} {teams['home']} vs {teams['away short']} {teams['away']}")
        return teams

    def _parse_date(self, date_time_element: str) -> datetime:
        date = datetime.datetime.now()

        if "Aujourd’hui à " in date_time_element:
            time_element = date_time_element.replace("Aujourd’hui à ", "")
        elif "Demain à " in date_time_element:
            time_element = date_time_element.replace("Demain à ", "")
            date += datetime.timedelta(days=1)
        else:
            time_element = date_time_element.split(' à ')[1]
            day_element = date_time_element.split(' à ')[0]

            # date like: '29 déc. 2024 à 16:45'
            if len(day_element.split()) == 3:
                dd, mm, yyyy = day_element.split()
                month = self.DATE_FORMAT['month'].index(mm) + 1

                date = date.replace(year=int(yyyy))
                date = date.replace(month=month)
                date = date.replace(day=int(dd))

            # date like: 'mardi à 19:35'
            else:
                # delta_day = (weekday_now + weekday_game + 2) % 7
                # exemple:
                #   now=dimanche(6), demain +1, mardi(1)+1 = +2, mecredi(2)+1 = +3
                #   now=jeudi(3), demain +1, samedi(5)+1 = +2, dimanche(6)+1 = +3

                weekday_game = self.DATE_FORMAT['day'].index(day_element)
                weekday_now = date.weekday()
                date += datetime.timedelta(days=(weekday_now + weekday_game + 2) % 7)

        hour, minute = time_element.split(':')
        date = date.replace(hour=int(hour))
        date = date.replace(minute=int(minute))
        date = date.replace(second=0)
        return date

    def _get_match_time(self, event) -> dict:
        date_time_element = event.find(self.CSS['tag']['date'], class_=self.CSS['class']['date'])
        self.logger.debug_log(f"CSS Bloc time found: {date_time_element}")

        # date_time_element: 'Aujourd’hui à 19:35', 'Demain à 01:00', 'mardi à 01:45' or '29 déc. 2024 à 19:00'
        date_time = self._parse_date(date_time_element.text)

        date = {
            "day": date_time.strftime("%Y-%m-%d"),
            "time": date_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "element": date_time_element.text,
        }
        self.logger.debug_log(f"Date found: {date['time']}")
        return date

    def _get_odds(self, event) -> dict:
        odds_elements = event.find_all(self.CSS['tag']['odd'], class_=self.CSS['class']['odd'])
        self.logger.debug_log(f"CSS Bloc odds found: {odds_elements}")

        if len(odds_elements) != 3:
            self.logger.debug_log(f"Not exactly 3 odds: {odds_elements}")

        odds = {
            "home": float(odds_elements[0].text.replace(',', '.')),
            "draw": float(odds_elements[1].text.replace(',', '.')),
            "away": float(odds_elements[2].text.replace(',', '.')),
        }

        self.logger.debug_log(f"Odds found: {odds}")
        return odds


def main():

    config = load_yaml("../config/bookmaker_config.yml")
    sport = "NHL"     # "NHL"

    # Initialize the scraper
    scraper = Pmu(config, sport, debug=True)
    extracted_data = scraper.extract_event_data()

    print("\nExtracted Data:")
    for event in extracted_data:
        print(event)


if __name__ == "__main__":
    main()