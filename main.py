from steam.webapi import WebAPI
import requests
import math
import logging
import argparse


class GameData:
    def __init__(self, details):
        self.details = details
        self.owners = []


class SteamHelper:
    @staticmethod
    def is_multiplayer(app_id: str) -> bool:
        """
        Checks if a game is multiplayer capable.
        Any error encountered on the way causes this method to return False.
        """
        result = False
        try:
            response = requests.get("https://store.steampowered.com/api/appdetails?appids=%s" % str(app_id),)
            if response.status_code == 200:
                details = response.json()[str(app_id)]["data"]
                result = any([cat for cat in details["categories"] if cat["description"] == "Multi-player"])
            else:
                logging.error("unexpected status code for app %s: %d" % (str(app_id), response.status_code))
        except KeyError:
            logging.error("can not retrieve app details for app %s" % str(app_id),)

        return result

    def __init__(self, web_api_key):
        self._api = WebAPI(web_api_key)

    def get_games_for_player(self, player_id: str) -> list:
        """
        Generates a list of games the player owns.
        """
        logging.info("retrieving games for player %s" % player_id,)
        return self._api.call("IPlayerService.GetOwnedGames", steamid=player_id, include_appinfo=True, include_played_free_games=True, appids_filter=[], include_free_sub=False)

    def get_games_for_players(self, player_ids: list[int]) -> dict:
        """
        Generates a dictionary of lists, where each key is one player id
        with the results of get_games_for_players as their value.
        """
        return {pid: self.get_games_for_player(pid) for pid in player_ids}

    def get_commons(self, player_ids: list[int]) -> dict:
        """
        Generates a dictionary where each key is the name of one game
        and the value is a GameData object for that game.
        """
        logging.info("finding commons for %d players" % len(player_ids,))
        games = self.get_games_for_players(player_ids)

        commons = {}
        for k, v in games.items():
            for game in v["response"]["games"]:
                name = game["name"]
                if name not in commons:
                    commons[name] = GameData(game)

                commons[name].owners.append(k)

        # already filter out games that are owned by only one person
        return {k: v for k, v in commons.items() if len(v.owners) > 1}

    def get_filtered_commons(self, player_ids: list[int], minimum_percentage=1, multiplayer_only=True) -> dict:
        """
        Generates a dictionary similar to the one from get_commons
        but filtered for several criterias.
        minimum_percentage: [0..1] the percentage of players that have to own the game. E.g. 0.6 means 60% of all players in player_id have to own the game for it to appear in the result
        multiplayer_only: whether single-player-only games should be filtered out
        """
        minimum_percentage = min(1, max(0.01, minimum_percentage))
        minimum_owners = math.ceil(minimum_percentage * len(player_ids))

        return {k: v for k, v in self.get_commons(player_ids).items() if len(v.owners) >= minimum_owners and not multiplayer_only or SteamHelper.is_multiplayer(v.details["appid"])}

    def format(self, player_ids, minimum_percentage=1, multiplayer_only=True) -> str:
        return "\n".join(["%s (%d/%d)" % (g.details["name"], len(g.owners), len(player_ids)) for g in sorted(self.get_filtered_commons(player_ids).values(), key=lambda game:len(game.owners), reverse=True)])


def main(args):
    multiplayer_only = args.multiplayer_only is True  # None is an option here
    percentage = args.percentage / 100

    helper = SteamHelper(args.api_key)
    print(helper.format(args.player_ids, minimum_percentage=percentage, multiplayer_only=multiplayer_only))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Finds games on Steam that are common to the passed players.")
    parser.add_argument("api_key", metavar="api_key", type=str, help="Steam WebAPI key. Can be obtained at https://steamcommunity.com/dev/apikey")
    parser.add_argument("player_ids", metavar="player_ids", type=int, nargs='+', help="list of SteamID64s (space separated)")
    parser.add_argument("--percentage", help="percentage of users that have to own a game for it to be considered common", type=int, choices=range(1, 101), default=100)
    parser.add_argument("--multiplayer-only", help="whether only mutliplayer games should be considered", type=bool, action=argparse.BooleanOptionalAction)
    args = parser.parse_args()
    main(args)
