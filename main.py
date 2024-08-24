import requests

from datetime import datetime
from time import sleep
from loguru import logger

from db import trim_db
from models import WinMap
from bot import send_message


logger.add("logs/debug.json", format="{time} {level} {message}",
           level="DEBUG", rotation="100 KB", compression="zip",
           serialize=True)


def get_message(win_map: WinMap, bet: str):
    league, team1, team2, timestamp, win1, win2 = win_map.values()
    timestamp = win_map["S"]
    game_date = datetime.fromtimestamp(timestamp).strftime("%d.%m %H:%M")
    message = f"{league} ({game_date})\n" \
              f"{team1} - {team2}\n" \
              f"\n" \
              f"{bet} -> {win1} & {win2}"
    send_message(message)
    try:
        logger.info(message)
        logger.info("message sent")
    except UnicodeEncodeError as ex:
        logger.error(f"unicode error, unknown char: {ex}")


def get_alter_message(win_map: WinMap, bet: str, coef: float):
    league, team1, team2, timestamp, win1, win2 = win_map.values()
    timestamp = win_map["S"]
    game_date = datetime.fromtimestamp(timestamp).strftime("%d.%m %H:%M")
    message = f"{league} ({game_date})\n" \
              f"{team1} - {team2}\n" \
              f"\n" \
              f"old odds: {bet} -> {coef}\n" \
              f"new odds: {bet} -> {win1}"
    send_message(message)
    try:
        logger.info(message)
        logger.info("message sent")
    except UnicodeEncodeError:
        logger.error("unicode error, unknown char")


def find_game(game_id: int, first_coef: float, win_map: WinMap, bet: str):
    with open("db.txt", "r", encoding="utf-8") as file:
        logger.debug("reading db")
        lines: dict[int, str] = {}
        res: list[int] = []
        for item in file.readlines():
            line, coef = item.strip().split()
            res.append(int(line))
            lines[int(line)] = coef
        if res.count(game_id) < 3:
            get_message(win_map, bet)
        if game_id == int(line) and str(first_coef) != coef:
            get_alter_message(win_map, bet, coef)

    with open("db.txt", "a", encoding="utf-8") as f:
        f.write(f"\n{game_id} {str(first_coef)}")
        logger.debug("writing bet to db")


def get_bet(match_result: dict[str, [str, int]], game_id: int):
    for game in match_result["Value"]:
        curr_id = game["I"]
        if curr_id == game_id:
            win_map: WinMap = \
                {
                    "L": game["L"],
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
                find_game(game_id, first_coef, win_map, bet)
                logger.debug("finding coefficients")


def get_match(result: dict[str, [str, int]]):
    for game in result["Value"][:7]:
        game_id = game["I"]
        champs = game["LI"]
        params: dict[str, str] = {
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
        logger.debug("getting info about match...")


def get_league():
    league_url = "https://1xstavka.ru/line/esports/2691803-cs-2-cct-europe-closed-qualifier"
    champs = league_url.split('/')[-1].split('-')[0]
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
    logger.debug("getting matches...")


if __name__ == "__main__":
    trim_db("C:\\Users\\melni\\PycharmProjects\\betboom_parser\\db.txt")
    while True:
        get_league()
        logger.info("sleeping...")
        sleep(1800)
