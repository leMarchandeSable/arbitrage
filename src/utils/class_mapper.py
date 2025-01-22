from utils.loaders import load_yaml, save_yaml
import datetime


class Mapper:
    def __init__(self, mapping_file: str = "team_mapping.yaml"):
        """
        Initialize the TeamNameMapper with a mapping file.
        :param mapping_file: Path to the YAML file containing team name mappings.
        """
        self.mapping_file = mapping_file
        self.team_mapper = load_yaml(self.mapping_file)["teams"]
        self.date_mapper = load_yaml(self.mapping_file)["date"]
        self.date_format = "%Y-%m-%d"
        self.datetime_format = "%Y-%m-%d %H:%M:%S"

    def map_team_name(self, sport: str, team_name: str) -> str:
        """
        Map a given team name to its standardized equivalent.
        :param sport: The sport category (e.g., NHL, AHL).
        :param team_name: The team name to map.
        :return: The standardized team name.
        """
        if sport not in self.team_mapper:
            raise ValueError(f"[ERROR] Sport '{sport}' not found in the mappings.")

        for standard_name, variations in self.team_mapper[sport].items():
            # check if the variation list is not empty for this standard name
            if not variations:
                continue
            if team_name in variations:
                return standard_name

        # If no mapping exists, log and optionally add it
        raise ValueError(f"[ERROR] Mapper unrecognized team name: {team_name} for '{sport}'")

    def update_mapper(self, sport: str, team_names: list):
        """
        Updates the mapping for a list of team names within a specific sport.

        This function ensures that team names are standardized and added to the mapping.
        If a team name is not already mapped, the user is prompted to input the standard
        team name, which is then added to the mapping.

        :param sport: (str) The sport to which the team names belong (e.g., "NHL", "AHL").
        :param team_names : A list of team names to update in the mapping.

        :raises ValueError: If an invalid or unmapped team name is encountered and no standard
            name is provided.

        Process:
            1. Iterates over the provided `team_names` list.
            2. Attempts to map each team name using `map_team_name`.
            3. If a `ValueError` is raised (indicating no mapping exists):
               - Prompts the user to input a standard team name.
               - Adds the new mapping using `_add_mapping`.
               - Reloads the mapping from the YAML file using `_load_mapping`.

        Example:
            >> update_mapper("NHL", ["Sharks", "Jets", "Avs"])
            [Input] The standard team name for 'Avs': Avalanche
            Successfully updates the mapping for "Sharks", "Jets", and "Avs".
        """

        for team_name in team_names:
            try:
                self.map_team_name(sport, team_name)
            except ValueError:
                standard_name = input(f"[Input] The standard team name for '{team_name}':")
                self._add_mapping(sport, standard_name, team_name)
                self.team_mapper = load_yaml(self.mapping_file)
        print("[INFO] All the current team names are mapped")

    def _add_mapping(self, sport: str, standard_name: str, variation_name: list, allow_new_standard_name: bool = False):
        """
        Add a new mapping or update an existing one.
        :param allow_new_standard_name: bool variable to accept to create a new standard team name
        :param sport: The sport category (e.g., NHL, AHL).
        :param standard_name: The standardized name.
        :param variation_name: A new variation of the standardized name.
        """
        if sport not in self.team_mapper:
            print(f"[INFO] New sport {sport} is added to the mapping file")
            self.team_mapper[sport] = {}

        if standard_name in self.team_mapper[sport]:
            # if there is no variation yet
            if not self.team_mapper[sport][standard_name]:
                self.team_mapper[sport][standard_name] = [variation_name]
            else:
                self.team_mapper[sport][standard_name].append(variation_name)

            # Remove duplicates
            self.team_mapper[sport][standard_name] = list(set(self.team_mapper[sport][standard_name]))
            print(f"[INFO] New variation name '{variation_name}' add for the team '{standard_name}'")
        else:
            if allow_new_standard_name:
                self.team_mapper[sport][standard_name] = [variation_name]
            print(f"[INFO] Variation name '{variation_name}' is not added: standard team '{standard_name}' is not recognize")

        save_yaml(self.team_mapper, self.mapping_file)

    # ------------------------------ Date parser -----------------------------------------------------------------------
    def map_date_unparse(self, bookmaker: str, date_unparse: str, scrapping_time: str = None) -> str:

        if scrapping_time is None:
            date_ref = datetime.datetime.now()
        else:
            date_ref = datetime.datetime.strptime(scrapping_time, self.datetime_format)

        if bookmaker == "Zebet":
            date = self._zebet_parse_date(date_unparse, date_ref)
        elif bookmaker == "Winamax":
            date = self._winamaw_parse_date(date_unparse, date_ref)
        elif bookmaker == "Netbet":
            date = self._netbet_parse_date(date_unparse, date_ref)
        else:
            raise ValueError(f"[ERROR] Unkown bookmaker name: {bookmaker}")

        return date.strftime(self.date_format)

    def _zebet_parse_date(self, date_unparse: str, date_ref: datetime.datetime) -> datetime.datetime:
        # exemple of date unparse:  ['À 01h00', 'Le 28/12 à 01h00', 'Demain à 04h00']

        if "À " in date_unparse:
            # unparse_date = date_ref
            date = date_ref
            pass
        elif "Demain à " in date_unparse:
            # unparse_date = date_ref + 1 day
            date = date_ref + datetime.timedelta(days=1)
        elif "Le " in date_unparse:
            # unparse_date = 'Le 28/12 à 01h00'
            dd, mm = date_unparse.split()[1].split('/')
            date = date_ref.replace(month=int(mm), day=int(dd))
        else:
            raise Exception(f"[ERROR] Unkown unparse date: {date_unparse}")
        return date

    def _winamaw_parse_date(self, date_unparse: str, date_ref: datetime.datetime) -> datetime.datetime:
        # exemple of date unparse: 'Aujourd’hui à 19:35', 'Demain à 01:00', 'mardi à 01:45' or '29 déc. 2024 à 19:00'

        if "Aujourd’hui à " in date_unparse:
            date = date_ref
        elif "Demain à " in date_unparse:
            date = date_ref + datetime.timedelta(days=1)
        elif len(date_unparse.split()) == 5:
            # date like: '29 déc. 2024 à 16:45'
            dd, mm, yyyy = date_unparse.split(' à ')[0].split()
            month = self.date_mapper['month'].index(mm) + 1
            date = date_ref.replace(year=int(yyyy), month=month, day=int(dd))
        elif len(date_unparse.split()) == 3:
            # date like: 'mardi à 19:35'

            # delta_day = (weekday_ref + weekday_game + 2) % 7
            # exemple:
            #   now=dimanche(6), demain +1, mardi(1)+1 = +2, mecredi(2)+1 = +3
            #   now=jeudi(3), demain +1, samedi(5)+1 = +2, dimanche(6)+1 = +3
            day = date_unparse.split(' à ')[0]
            weekday_game = self.date_mapper['day'].index(day)
            weekday_ref = date_ref.weekday()
            date = date_ref + datetime.timedelta(days=(weekday_ref + weekday_game + 2) % 7)
        else:
            raise Exception(f"[ERROR] Unkown unparse date: {date_unparse}")

        return date

    def _netbet_parse_date(self, date_unparse: str, date_ref: datetime.datetime) -> datetime.datetime:
        # exemple of date unparse: 'LIVE dans 25 min', 'mar. 24 déc. 02:00'

        try:
            if "LIVE" in date_unparse:
                date = date_ref
            elif len(date_unparse.split()) == 4:
                dd = date_unparse.split()[1]
                mm = date_unparse.split()[2]
                month = self.date_mapper["month"].index(mm) + 1
                date = date_ref.replace(day=int(dd), month=month)
            else:
                raise Exception(f"[ERROR] Unkown unparse date: {date_unparse}")

        except ValueError:
            raise ValueError(f"[ERROR] Impossible to find '{mm}' in date mapper: {self.date_mapper['month']}")
        except IndexError:
            raise IndexError(f"[ERROR] Impossible to index :{date_unparse.split()}")
        except Exception as e:
            raise e
        return date


def main():
    # --------------------- CONST ---------------------

    mapper = Mapper("../../data/mapping.yml")

    # mapper.update_mapper(sport, team_names)
    # mapper._netbet_parse_date("coco", datetime.datetime.now())


if __name__ == "__main__":
    main()
