import requests

resp = requests.get("https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-08-03")
data = resp.json()
print(data)

import json
print(json.dumps(data, indent=2))

games = data["dates"][0]["games"]

for game in games:
    game_id = game["gamePk"]
    date = game["officialDate"]
    away_team = game["teams"]["away"]["team"]["name"]
    away_score = game["teams"]["away"]["score"]
    home_team = game["teams"]["home"]["team"]["name"]
    home_score = game["teams"]["home"]["score"]
    
    print(f"{game_id}: {away_team} {away_score} @ {home_team} {home_score}")

game_id = 823520
resp = requests.get(f"https://statsapi.mlb.com/api/v1.1/game/{game_id}/feed/live")
game_data = resp.json()

# Boxscore lives under liveData
boxscore = game_data["liveData"]["boxscore"]

# Just look at the away team's batters for now
away_team = boxscore["teams"]["away"]
print(away_team.keys())

players = away_team["players"]

# Grab just the first player ID in the dict, to inspect one entry
first_player_key = list(players.keys())[0]
print(first_player_key)
print(players[first_player_key])

for player_key, player_data in players.items():
    name = player_data["person"]["fullName"]
    batting = player_data["stats"]["batting"]
    pitching = player_data["stats"]["pitching"]

    if batting.get("atBats", 0) > 0:
        print(f"BATTER: {name} — {batting['hits']} hits, {batting['homeRuns']} HR, {batting['rbi']} RBI")

    if pitching.get("inningsPitched", "0") != "0.0" and pitching.get("gamesPitched", 0) > 0:
        print(f"PITCHER: {name} — {pitching['inningsPitched']} IP, {pitching['strikeOuts']} K, {pitching['earnedRuns']} ER")

home_team = boxscore["teams"]["home"]
home_players = home_team["players"]

for player_key, player_data in home_players.items():
    name = player_data["person"]["fullName"]
    batting = player_data["stats"]["batting"]
    pitching = player_data["stats"]["pitching"]

    if batting.get("atBats", 0) > 0:
        print(f"BATTER: {name} — {batting['hits']} hits, {batting['homeRuns']} HR, {batting['rbi']} RBI")

    if pitching.get("inningsPitched", "0") != "0.0" and pitching.get("gamesPitched", 0) > 0:
        print(f"PITCHER: {name} — {pitching['inningsPitched']} IP, {pitching['strikeOuts']} K, {pitching['earnedRuns']} ER")
        