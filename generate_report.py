from db import get_connection

def get_game_summary(conn, game_id):
    """Pull the core info needed to build a recap for one game."""
    cursor = conn.cursor()

    cursor.execute("""
        SELECT g.game_date, g.home_score, g.away_score,
               ht.name AS home_team, at.name AS away_team
        FROM games g
        JOIN teams ht ON g.home_team_id = ht.team_id
        JOIN teams at ON g.away_team_id = at.team_id
        WHERE g.game_id = ?
    """, (game_id,))
    game = cursor.fetchone()

    cursor.execute("""
        SELECT p.full_name, b.hits, b.home_runs, b.rbi
        FROM batting_stats b
        JOIN players p ON b.player_id = p.player_id
        WHERE b.game_id = ?
        ORDER BY b.rbi DESC, b.hits DESC
        LIMIT 1
    """, (game_id,))
    top_batter = cursor.fetchone()

    return game, top_batter

def build_recap(game, top_batter):
    game_date, home_score, away_score, home_team, away_team = game

    if home_score > away_score:
        winner, winner_score = home_team, home_score
        loser, loser_score = away_team, away_score
    else:
        winner, winner_score = away_team, away_score
        loser, loser_score = home_team, home_score

    recap = f"On {game_date}, the {winner} defeated the {loser} {winner_score}-{loser_score}."

    if top_batter:
        name, hits, home_runs, rbi = top_batter
        recap += f" {name} led the offense, going {hits}-for-the-day with {home_runs} home run(s) and {rbi} RBI."

    return recap

def save_report(conn, game_id, recap):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reports WHERE game_id = ?", (game_id,))
    cursor.execute("""
        INSERT INTO reports (game_id, headline, body)
        VALUES (?, ?, ?)
    """, (game_id, None, recap))
    conn.commit()

if __name__ == "__main__":
    conn = get_connection()

    cursor = conn.cursor()
    cursor.execute("SELECT game_id FROM games")
    game_ids = [row[0] for row in cursor.fetchall()]

    for game_id in game_ids:
        game, top_batter = get_game_summary(conn, game_id)
        recap = build_recap(game, top_batter)
        save_report(conn, game_id, recap)
        print(f"Game {game_id}: {recap}")

    conn.close()



