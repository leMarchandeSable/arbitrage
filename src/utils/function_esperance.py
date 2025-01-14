import pandas as pd

from utils.class_databasemanager import DatabaseManager
from utils.loaders import load_config
from itertools import product


def calc_esperance(odd_1: float, odd_N: float, odd_2: float) -> float:
    """
    Calculates the arbitrage possibility given three odds.
    """
    e = 1/odd_1 + 1/odd_N + 1/odd_2
    if e < 1:
        raise f"Wow arbitrage possible: {e}"
    return e


def find_arbitrage(df: pd.DataFrame):

    # Sort by Game ID, Bookmaker, and Timestamp (most recent first)
    df_sorted = df.sort_values(by="scrapping_time", ascending=False)
    # Group by unique game details and then take the first row for each bookmaker
    df_grouped = df_sorted.groupby(["Date", "Home Team Std", "Away Team Std", "Bookmaker"]).first()
    # print(df_group_game.to_string())        # Debug

    # Group by unique game details (excluding Bookmaker) to organize odds
    for _, events in df_grouped.groupby(["Date", "Home Team Std", "Away Team Std"]):
        """
            Example structure of events:
            Date       Home Team Std           Away Team Std          Bookmaker                                                                 
            2025-01-11 WPG - Winnipeg Jets     LAK - Los Angeles Kings
                                      Netbet   2025-01-11T02:00:00Z  2.37 3.90 2.40  2025-01-11 00:05:58
                                      Winamax  2025-01-11T02:05:00Z  2.40 3.95 2.45  2025-01-10 22:56:43
                                      Zebet    2025-01-11T02:00:00Z  2.40 3.95 2.45  2025-01-10 23:48:13
        """
        # print(events.to_string())

        # Extract odds for each bookmaker
        odds = {
            bookmaker: event[["Home Odd", "Draw Odd", "Away Odd"]].values
            for (date, home_team, away_team, bookmaker), event in events.iterrows()
        }

        home_odds = [(bookmaker, odds[0]) for bookmaker, odds in odds.items()]
        draw_odds = [(bookmaker, odds[1]) for bookmaker, odds in odds.items()]
        away_odds = [(bookmaker, odds[2]) for bookmaker, odds in odds.items()]
        combination = list(product(home_odds, draw_odds, away_odds))

        for combo in combination:
            try:
                arb = calc_esperance(combo[0][1], combo[1][1], combo[2][1])
            except Exception as e:
                print(e)
                print(combo)


if __name__ == "__main__":
    config = load_config("../../config/bookmaker_config.yml")
    db = DatabaseManager("../../data/database.csv")

    find_arbitrage(db.data)
