import requests
from db import get_connection

def fetch_schedule(date):
    """Get all games played on a given date (format: YYYY-MM-DD)."""
    resp = requests.get(f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}")
    data = resp.json()
    if not data["dates"]:
        return []
    return data["dates"][0]["games"]

def save_game(conn, game):
    """Insert a game's basic info + both teams into the database."""
    cursor = conn.cursor()

    game_id = game["gamePk"]
    game_date = game["officialDate"]
    status = game["status"]["detailedState"]

    away = game["teams"]["away"]
    home = game["teams"]["home"]

    away_team_id = away["team"]["id"]
    away_team_name = away["team"]["name"]
    away_score = away.get("score")

    home_team_id = home["team"]["id"]
    home_team_name = home["team"]["name"]
    home_score = home.get("score")

    # Insert teams first (games references them)
    cursor.execute("""
        INSERT OR IGNORE INTO teams (team_id, name, abbreviation)
        VALUES (?, ?, ?)
    """, (away_team_id, away_team_name, None))

    cursor.execute("""
        INSERT OR IGNORE INTO teams (team_id, name, abbreviation)
        VALUES (?, ?, ?)
    """, (home_team_id, home_team_name, None))

    # Insert the game itself
    cursor.execute("""
        INSERT OR REPLACE INTO games
        (game_id, game_date, home_team_id, away_team_id, home_score, away_score, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (game_id, game_date, home_team_id, away_team_id, home_score, away_score, status))

    conn.commit()

def fetch_boxscore(game_id):
    """Get the full box score for a single game."""
    resp = requests.get(f"https://statsapi.mlb.com/api/v1.1/game/{game_id}/feed/live")
    data = resp.json()
    return data["liveData"]["boxscore"]

def save_player_stats(conn, game_id, team_id, players):
    """Insert batting and pitching stat lines for one team's players in one game."""
    cursor = conn.cursor()

    # Clear any existing stats for this game+team combo, so reruns don't duplicate
    player_ids_for_team = [p["person"]["id"] for p in players.values()]
    placeholders = ",".join("?" * len(player_ids_for_team))
    if player_ids_for_team:
        cursor.execute(f"""
            DELETE FROM batting_stats
            WHERE game_id = ? AND player_id IN ({placeholders})
        """, (game_id, *player_ids_for_team))
        cursor.execute(f"""
            DELETE FROM pitching_stats
            WHERE game_id = ? AND player_id IN ({placeholders})
        """, (game_id, *player_ids_for_team))
        
    for player_key, player_data in players.items():
        player_id = player_data["person"]["id"]
        player_name = player_data["person"]["fullName"]

        # Make sure the player exists in the players table
        cursor.execute("""
            INSERT OR IGNORE INTO players (player_id, full_name, team_id)
            VALUES (?, ?, ?)
        """, (player_id, player_name, team_id))

        batting = player_data["stats"]["batting"]
        pitching = player_data["stats"]["pitching"]

        if batting.get("atBats", 0) > 0:
            cursor.execute("""
                INSERT INTO batting_stats
                (game_id, player_id, at_bats, hits, home_runs, rbi, runs, walks, strikeouts)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                game_id, player_id,
                batting.get("atBats"), batting.get("hits"), batting.get("homeRuns"),
                batting.get("rbi"), batting.get("runs"), batting.get("baseOnBalls"),
                batting.get("strikeOuts")
            ))

        if pitching.get("gamesPitched", 0) > 0:
            cursor.execute("""
                INSERT INTO pitching_stats
                (game_id, player_id, innings_pitched, hits_allowed, runs_allowed, earned_runs, walks, strikeouts, decision)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                game_id, player_id,
                pitching.get("inningsPitched"), pitching.get("hits"), pitching.get("runs"),
                pitching.get("earnedRuns"), pitching.get("baseOnBalls"), pitching.get("strikeOuts"),
                None  # we'll figure out win/loss/save decision separately later
            ))

    conn.commit()

if __name__ == "__main__":
    date = "2026-08-03"
    games = fetch_schedule(date)
    print(f"Found {len(games)} games on {date}")

    conn = get_connection()
    for game in games:
        save_game(conn, game)
        game_id = game["gamePk"]

        boxscore = fetch_boxscore(game_id)
        away_team_id = game["teams"]["away"]["team"]["id"]
        home_team_id = game["teams"]["home"]["team"]["id"]

        save_player_stats(conn, game_id, away_team_id, boxscore["teams"]["away"]["players"])
        save_player_stats(conn, game_id, home_team_id, boxscore["teams"]["home"]["players"])

        print(f"Saved game {game_id} with full box score")
    conn.close()

