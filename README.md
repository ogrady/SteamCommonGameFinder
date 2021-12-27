# SteamCommonGameFinder
Utility to find games that are owned by all (or at least some) of the players you pass into this programm.

You can already find some utilities for this purpose online, such as [here](https://www.mysteamgauge.com/friends). But all tools I found either lacked the capability of entering more than two players or were simply broken at the time.
This tool works from the command line and works with an indefinite number of players. Note that all players should have their owned games set to be publicly viewable -- I have not tested what happens when one of them sets their profile to private.

## Installation
```sh
pip3 install -r requirements.txt
```

## Running
The bare minimum to run the tool requires you to pass a [WebAPI key](https://steamcommunity.com/dev/apikey) as first positional argument and a series of SteamID64 as following arguments. Using profile names is not supported at the moment, but you can use tools such as [SteamIDFinder](https://www.steamidfinder.com/) to convert a profile name to a SteamID64.

```sh
python3 main.py AAAAAAAAAAA 12345 6789 13579 24680
```

Would look for games that are owned by all four players with the IDs `12345`, `6789`, `13579`, and `24680`.

```sh
python3 main.py AAAAAAAAAAA 12345 6789 13579 24680 --multiplayer-only
```

Would do the same, but filter out games that are not marked as multiplayer games. This is no guarantee that the games will allow for all players to play at the same time, as it could show games that allow up to two players while you are looking for games for four players.

```sh
python3 main.py AAAAAAAAAAA 12345 6789 13579 24680 --percentage=75
``` 

Looks for games that are owned by at least 75% of the passed players. In the above example, you would find games that are owned by at least three players, so you have to only buy one more copy to be able to play together.