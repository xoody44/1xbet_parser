from typing import Union

import requests

from datetime import datetime
from time import sleep
from loguru import logger

from db import trim_db
from models import WinMap
from bot import send_message
from app_tkinter import show_input_window


logger.add("logs/debug.json", format="{time} {level} {message}",
           level="DEBUG", rotation="100 KB", compression="zip",
           serialize=True)

league_url, match_format, sleep_time = show_input_window()


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
        logger.critical(f"unicode error, unknown char: {ex}")


def get_alter_message(win_map: WinMap, bet: str, coef: Union[float, str]):
    league, team1, team2, timestamp, win1, win2 = win_map.values()
    timestamp = win_map["S"]
    game_date = datetime.fromtimestamp(timestamp).strftime("%d.%m %H:%M")
    message = f"{league} ({game_date})\n" \
              f"{team1} - {team2}\n" \
              f"\n" \
              f"old odds: {bet} -> {coef}\n" \
              f"new odds: {bet} -> {win1}"
    try:
        send_message(message)
        logger.info(message)
        logger.info("message sent")
    except UnicodeEncodeError:
        logger.error("unicode error, unknown char. probably u2060 in text")
        message = message.replace("\u2060", "")
        send_message(message)


def find_game(game_id: int, first_coef: float, win_map: WinMap, bet: str, m_format: str):
    if not first_coef:
        logger.error("cannot find coefficient")
        return 0
    with open("db.txt", "r", encoding="utf-8") as file:
        logger.debug("reading db")
        lines: dict[int, str] = {}
        res: list[int] = []
        for item in file.readlines():
            line, coef = item.strip().split()
            res.append(int(line))
            lines[int(line)] = coef
        if res.count(game_id) < int(m_format):
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
            win_map: WinMap = {
                "L": game["L"],
                "O1": game["O1"],
                "O2": game["O2"],
                "S": game["S"]
            }
            bets = game["SG"]
            for item in bets:
                bet = item["PN"]
                first_coef = None
                second_coef = None
                for node in item["E"]:
                    table_cell = node["T"]
                    if 1 == table_cell:
                        first_coef = node["C"]
                        win_map["win1"] = first_coef
                    if 3 == table_cell:
                        second_coef = node["C"]
                        win_map["win2"] = second_coef
                if first_coef is not None and second_coef is not None:
                    find_game(game_id, first_coef, win_map, bet, match_format)
                    logger.debug("finding coefficients")


def get_match(result: dict[str, [str, int]]):
    for game in result["Value"][:5]:
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


def get_league(l_url: str):
    try:
        url = l_url
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
        logger.debug("getting matches...")
    except Exception as ex:
        logger.critical("url doesnt written")
        logger.critical(ex)


if __name__ == "__main__":
    trim_db()
    while True:
        get_league(league_url)
        logger.info("sleeping...")
        sleep(int(sleep_time))
