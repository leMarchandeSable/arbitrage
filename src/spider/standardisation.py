from utils.loaders import *
from difflib import get_close_matches, SequenceMatcher
from itertools import product, combinations


def get_combo_ratio(combo: tuple) -> float:
    similarity = 0
    for a, b in combinations(combo, 2):
        similarity += SequenceMatcher(None, a, b).ratio()
    return similarity / len(combo)


def ravel(d):
    d_ravel = {}
    for sport_name in d.keys():
        for category_name in d[sport_name].keys():
            for tournament_name in d[sport_name][category_name].keys():
                k = sport_name + " " + category_name + " " + tournament_name
                d_ravel[k] = d[sport_name][category_name][tournament_name]
    return d_ravel


urls = {
    "winamax": load_json("winamax_urls.json"),
    "zebet": load_json("zebet_urls.json"),
    "netbet": load_json("netbet_urls.json"),
}

# winamax dict_keys(['automobile', 'badminton', 'baseball', 'basketball', 'biathlon', 'boxe', 'cyclisme', 'football', 'football americain', 'football australien', 'handball', 'hockey sur glace', 'mma', 'rugby a 7', 'rugby a xiii', 'rugby a xv', 'tennis', 'volley ball'])
# zebet dict_keys(['aussie rules', 'badminton', 'baseball', 'basketball', 'biathlon', 'boxe', 'foot americain', 'football', 'formule 1', 'golf', 'handball', 'hockey sur glace', 'nascar', 'rugby a 7', 'rugby a xiii', 'rugby', 'ski alpin', 'ski de fond', 'snooker', 'tennis', 'ufc mma', 'volley ball'])
# netbet dict_keys(['badminton', 'baseball', 'basketball', 'biathlon', 'boxe', 'cyclisme', 'foot us', 'football', 'golf', 'handball', 'hockey glace', 'moto', 'rugby a xiii', 'rugby', 'ski alpin', 'sport automobile', 'tennis', 'volleyball'])

not_betable_sport_w = ['automobile', 'biathlon', 'cyclisme', 'formule 1', 'golf', 'moto', 'ski alpin', 'ski de fond']
not_betable_sport_n = ['biathlon', 'cyclisme', 'formule 1', 'golf', 'moto', 'ski alpin', 'sport automobile']
not_betable_sport_z = ['biathlon', 'formule 1', 'golf', 'moto', 'nascar', 'ski alpin', 'ski de fond']

sport = "football"
category = "france"
l = []


for combo in product(urls.keys()):
    ratio = get_combo_ratio(combo)
    if ratio > 0.8:
        print(round(ratio, 2), " - ".join(combo))


"""
for bookmaker, sport in urls.items():
    print(bookmaker)
    link = []
    for category in sport["football"].keys():
        for tournament in sport["football"][category].keys():
            link.append(sport["football"][category][tournament])
    print(link)
    print()
"""
