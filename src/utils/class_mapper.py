from utils.loaders import load_config
import yaml


class Mapper:
    def __init__(self, mapping_file: str = "team_mapping.yaml"):
        """
        Initialize the TeamNameMapper with a mapping file.
        :param mapping_file: Path to the YAML file containing team name mappings.
        """
        self.mapping_file = mapping_file
        self.mapping = self._load_mapping()

    def _load_mapping(self) -> dict:
        """
        Load team name mappings from a YAML file.
        :return: A dictionary containing team name mappings.
        """
        try:
            with open(self.mapping_file, "r") as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            raise ValueError(f"[INFO] Mapping file '{self.mapping_file}' not found. Creating a new one.")
        except yaml.YAMLError as e:
            raise ValueError(f"[ERROR] Failed to parse YAML file: {e}")

    def _save_mapping(self):
        """
        Save the current mapping to the YAML file.
        """
        with open(self.mapping_file, "w") as file:
            yaml.dump(self.mapping, file)

    def map_team_name(self, sport: str, team_name: str) -> str:
        """
        Map a given team name to its standardized equivalent.
        :param sport: The sport category (e.g., NHL, AHL).
        :param team_name: The team name to map.
        :return: The standardized team name.
        """
        if sport not in self.mapping:
            raise ValueError(f"[ERROR] Sport '{sport}' not found in the mappings.")

        for standard_name, variations in self.mapping[sport].items():
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
                self.mapping = self._load_mapping()
        print("[INFO] All the current team names are mapped")

    def _add_mapping(self, sport: str, standard_name: str, variation_name: list, allow_new_standard_name: bool = False):
        """
        Add a new mapping or update an existing one.
        :param allow_new_standard_name: bool variable to accept to create a new standard team name
        :param sport: The sport category (e.g., NHL, AHL).
        :param standard_name: The standardized name.
        :param variation_name: A new variation of the standardized name.
        """
        if sport not in self.mapping:
            print(f"[INFO] New sport {sport} is added to the mapping file")
            self.mapping[sport] = {}

        if standard_name in self.mapping[sport]:
            # if there is no variation yet
            if not self.mapping[sport][standard_name]:
                self.mapping[sport][standard_name] = [variation_name]
            else:
                self.mapping[sport][standard_name].append(variation_name)

            # Remove duplicates
            self.mapping[sport][standard_name] = list(set(self.mapping[sport][standard_name]))
            print(f"[INFO] New variation name '{variation_name}' add for the team '{standard_name}'")
        else:
            if allow_new_standard_name:
                self.mapping[sport][standard_name] = [variation_name]
            print(f"[INFO] Variation name '{variation_name}' is not added: standard team '{standard_name}' is not recognize")

        self._save_mapping()


def main():
    # --------------------- CONST ---------------------
    config = load_config("../config/bookmaker_config.yml")
    sport = "NHL"

    # db = DatabaseManager(config["path"]["database"])
    # mapping = Mapper(config["path"]["mapping"])
    # db = DatabaseManager("../data/database.csv")
    # mapping = Mapper("../../data/mapping.yml")

    # team_names = list(db.data["Home Team"]) + list(db.data["Away Team"])
    # mapping.update_mapper(sport, team_names)


if __name__ == "__main__":
    main()





