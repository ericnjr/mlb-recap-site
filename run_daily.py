from datetime import date, timedelta
from db import get_connection, init_db
from fetch_games import fetch_schedule, fetch_boxscore, save_game, save_player_stats
from generate_report import get_game_summary, build_recap, save_report

def run_for_date(target_date):
    print(f"Running pipeline for {target_date}")

    init_db()  # safe to call every time, only creates tables if missing
    conn = get_connection()

    games = fetch_schedule(target_date)
    print(f"Found {len(games)} games")

    for game in games:
        game_id = game["gamePk"]

        # Skip games that aren't finished yet
        if game["status"]["detailedState"] != "Final":
            print(f"Skipping game {game_id} — not final yet")
            continue

        save_game(conn, game)

        boxscore = fetch_boxscore(game_id)
        away_team_id = game["teams"]["away"]["team"]["id"]
        home_team_id = game["teams"]["home"]["team"]["id"]

        save_player_stats(conn, game_id, away_team_id, boxscore["teams"]["away"]["players"])
        save_player_stats(conn, game_id, home_team_id, boxscore["teams"]["home"]["players"])

        game_summary, top_batter = get_game_summary(conn, game_id)
        recap = build_recap(game_summary, top_batter)
        save_report(conn, game_id, recap)

        print(f"Processed game {game_id}")

    conn.close()
    print("Done.")

if __name__ == "__main__":
    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    run_for_date(yesterday)

