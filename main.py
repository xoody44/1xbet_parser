from typing import Any
from datetime import datetime
from bot import send_message
from time import sleep

import requests


def get_message(win_map, bet):
    league, team1, team2, timestamp, win1, win2 = win_map.values()
    timestamp = win_map["S"]
    game_date = datetime.fromtimestamp(timestamp).strftime("%d.%m %H:%M")
    message = f"{league} ({game_date})\n" \
              f"{team1} - {team2}\n" \
              f"\n" \
              f"{bet} -> {win1} & {win2}"
    send_message(message)
    print(message)
    print("=" * 30)


def get_alter_message(win_map, bet, coef):
    league, team1, team2, timestamp, win1, win2 = win_map.values()
    timestamp = win_map["S"]
    game_date = datetime.fromtimestamp(timestamp).strftime("%d.%m %H:%M")
    message = f"{league} ({game_date})\n" \
              f"{team1} - {team2}\n" \
              f"\n" \
              f"old odds: {bet} -> {coef}\n" \
              f"new odds: {bet} -> {win1}"
    send_message(message)
    print(message)
    print("=" * 30)


def find_game(game_id, first_coef, second_coef, win_map, bet):
    with open("db.txt", "r") as file:
        lines = {}
        res = []
        for item in file.readlines():
            line, coef = item.strip().split()
            res.append(int(line))
            lines[int(line)] = coef
        if res.count(game_id) < 3:
            get_message(win_map, bet)
        if game_id == int(line) and str(first_coef) != coef:
            get_alter_message(win_map, bet, coef)
    with open("db.txt", "a") as f:
        f.write(f"\n{game_id} {str(first_coef)}")


def get_bet(match_result, game_id):
    for game in match_result["Value"]:
        curr_id = game["I"]
        if curr_id == game_id:
            win_map: dict[str, Any] = {"L": game["L"],
                                       "O1": game["O1"],
                                       "O2": game["O2"],
                                       "S": game["S"]
                                       }

            bets = game["SG"]
            for item in bets:
                bet = item["PN"]
                for node in item["E"]:
                    table_cell = node["T"]
                    if 1 == table_cell:
                        first_coef = node["C"]
                        win_map["win1"] = first_coef
                    if 3 == table_cell:
                        second_coef = node["C"]
                        win_map["win2"] = second_coef
                find_game(game_id, first_coef, second_coef, win_map, bet)
            print("-" * 30)


def get_match(result):
    for game in result["Value"][:7]:
        game_id = game["I"]
        champs = game["LI"]
        params = {
            'sports': '40',
            'champs': champs,
            'count': '50',
            'tf': '2200000',
            'tz': '5',
            'antisports': '188',
            'mode': '4',
            'subGames': game_id,
            'country': '1',
            'partner': '51',
            'getEmpty': 'true',
            'gr': '44',
        }

        response = requests.get('https://1xstavka.ru/LineFeed/Get1x2_VZip', params=params)
        match_result = response.json()
        get_bet(match_result, game_id)


def main():
    url = "https://1xstavka.ru/line/esports/2744847-dota-2-res-regional-series-latam-4"
    champs = url.split('/')[-1].split('-')[0]
    params = {
        'sports': '40',
        'champs': champs,
        'count': '50',
        'tf': '2200000',
        'tz': '5',
        'antisports': '188',
        'mode': '4',
        'country': '1',
        'partner': '51',
        'getEmpty': 'true',
        'gr': '44',
    }

    response = requests.get('https://1xstavka.ru/LineFeed/Get1x2_VZip', params=params)
    result = response.json()
    get_match(result)


if __name__ == "__main__":
    while True:
        main()
        sleep(1800)
