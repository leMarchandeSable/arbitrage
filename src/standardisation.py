import pandas

from utils.loaders import *
from difflib import get_close_matches, SequenceMatcher
from itertools import product, combinations, permutations
from utils.class_databasemanager import DatabaseManager
from utils.function_matchs import clean_key
import numpy as np


def calc_esperance(odds: list) -> float:
    """
    Calculates the arbitrage possibility given three odds.
    """
    return sum([1 / odd for odd in odds])


def get_similarity(combo) -> float:

    if len(combo) == 1:
        return 1

    similarity = 0
    n = 0
    for a, b in combinations(combo, 2):
        similarity += SequenceMatcher(None, a, b).ratio()
        n += 1
    return similarity / n


def analyse_linked_events(linked_events):
    for group_id, linked_event in linked_events.items():

        nb_game_found = len(linked_event)
        nb_game_found_str = f"Game found: {nb_game_found}"
        group_id_str = f"Group ID: ({' - '.join(group_id)})"
        rank_games = list(map(lambda x: len(x), linked_event))
        rank_ratios = [rank_games.count(rank) / nb_game_found for rank in range(nb_bookmakers, 0, -1)]
        # print(group_id_str)
        # print(linked_event)
        # print(rank_games)
        # print(rank_ratios)
        rank_ratios_str = [f"Rank {i + 1}: {100 * rank:.0f} %" for i, rank in enumerate(rank_ratios)]
        # print(" ".join(rank_ratios_str))
        print(f'{nb_game_found_str:<20}' + " ".join(map(lambda x: f"{x:<20}", rank_ratios_str)) + group_id_str)

        # ---------------------------------------------------------------------------


def group_events(data: pandas.DataFrame, nb_bookmakers: int, similarity_threshold: float = 0.6) -> dict:

    # linked_events is a list of indices, represents the game events that are the same on different bookmaker
    # indices is a tuple of row index of length 'combo_size'
    linked_events = {}

    # Iterate through each group of event group by parse argument
    for group_id, event_group in data.groupby(["Date", "Sport", "Category"]):
        # group_id : ("2025-01-25", "basketball", "allemagne"), ('2025-01-25', 'basketball', 'etats unis')

        if "football" not in group_id:
            continue

        # ---------------------------------------------------------------------------
        teams_group = []
        # Populate teams_group for the current group with db index and team names
        for index, row in event_group.iterrows():
            team_names = clean_key(row["Home Team Unparse"]) + " - " + clean_key(row["Away Team Unparse"])
            teams_group.append((index, team_names))
        # ---------------------------------------------------------------------------

        # linked_events is a list of indices, represents the game events that are the same on different bookmaker
        # indices is a tuple of row index of length 'combo_size'
        linked_event = []
        # combo_size is a variable between nb_bookmaker and 0, that set the number of bookmakers inside 'team_combo'
        for combo_size in range(nb_bookmakers, 0, -1):

            # loop through all the combination of team_group until there is no valid combo in the pool
            combo_found = True
            while combo_found:

                combo_pool = []
                for team_combo in combinations(teams_group, combo_size):

                    # a valid combo can't use index row that are already use
                    indices, teams = zip(*team_combo)
                    if any(idx in sum(linked_event, []) for idx in indices):
                        continue

                    # a valid combo don't have twice the same bookmaker
                    bookmakers = db.data["Bookmaker"][list(indices)]
                    if len(set(bookmakers)) != len(bookmakers):
                        continue

                    # calculate the similarity score of the combination
                    similarity = get_similarity(teams)
                    combo_pool.append((similarity, team_combo))

                if not combo_pool:
                    break

                # Sort by similarity in descending order
                combo_pool.sort(key=lambda x: x[0], reverse=True)
                best_similarity, best_team_combo = combo_pool[0]

                # if the best combination is similar enough, loop again with the same 'combo_size'
                if best_similarity > similarity_threshold:
                    indices, teams = zip(*best_team_combo)
                    linked_event.append(list(indices))
                else:
                    combo_found = False
        linked_events[group_id] = linked_event
        # ---------------------------------------------------------------------------
    return linked_events


def find_arbitrage(linked_events):
    for linked_event in linked_events:
        """
        if linked_event != [621, 1229, 2072]:
            continue
        """

        if db.data.loc[linked_event, ["Home Odd", "Draw Odd", "Away Odd"]].isna().any(axis=None):
            continue

        odds = [
            db.data.loc[linked_event, ["Home Odd"]].values,
            db.data.loc[linked_event, ["Draw Odd"]].values,
            db.data.loc[linked_event, ["Away Odd"]].values,
        ]

        possible_arbitrage = []
        for combo in product(*odds):
            arb = calc_esperance(combo)
            if arb < 1:
                possible_arbitrage.append((arb, combo))

        possible_arbitrage.sort(key=lambda x: x[0])
        if possible_arbitrage:
            arb, combo = possible_arbitrage[0]
            print('-' * 50)
            print(db.data.iloc[linked_event].to_string())
            print(combo, arb)
            print('-' * 50)


if __name__ == '__main__':

    db = DatabaseManager("../data/database.csv")
    nb_bookmakers = 3
    similarity_threshold = 0.6

    linked_events = group_events(db.data, nb_bookmakers, similarity_threshold)
    # analyse_linked_events(linked_events)
    # find_arbitrage(linked_events)


