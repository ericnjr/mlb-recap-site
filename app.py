from flask import Flask, render_template
from db import get_connection

app = Flask(__name__)

@app.route("/")
def index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT g.game_id, g.game_date, ht.name AS home_team, at.name AS away_team,
               g.home_score, g.away_score
        FROM games g
        JOIN teams ht ON g.home_team_id = ht.team_id
        JOIN teams at ON g.away_team_id = at.team_id
        ORDER BY g.game_date DESC
    """)
    games = cursor.fetchall()
    conn.close()
    return render_template("index.html", games=games)

@app.route("/game/<int:game_id>")
def game_detail(game_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT g.game_date, ht.name AS home_team, at.name AS away_team,
               g.home_score, g.away_score
        FROM games g
        JOIN teams ht ON g.home_team_id = ht.team_id
        JOIN teams at ON g.away_team_id = at.team_id
        WHERE g.game_id = ?
    """, (game_id,))
    game = cursor.fetchone()

    cursor.execute("SELECT body FROM reports WHERE game_id = ? LIMIT 1", (game_id,))
    report = cursor.fetchone()

    cursor.execute("""
        SELECT p.full_name, b.at_bats, b.hits, b.home_runs, b.rbi, b.runs, b.walks, b.strikeouts
        FROM batting_stats b
        JOIN players p ON b.player_id = p.player_id
        WHERE b.game_id = ?
        ORDER BY b.rbi DESC
    """, (game_id,))
    batters = cursor.fetchall()

    cursor.execute("""
        SELECT p.full_name, pi.innings_pitched, pi.hits_allowed, pi.earned_runs, pi.strikeouts, pi.walks
        FROM pitching_stats pi
        JOIN players p ON pi.player_id = p.player_id
        WHERE pi.game_id = ?
        ORDER BY pi.innings_pitched DESC
    """, (game_id,))
    pitchers = cursor.fetchall()

    conn.close()
    return render_template("game_detail.html", game=game, report=report, batters=batters, pitchers=pitchers)

if __name__ == "__main__":
    app.run(debug=True)
