import sqlite3

def get_connection():
    return sqlite3.connect("mlb.db")

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teams (
        team_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        abbreviation TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS games (
        game_id INTEGER PRIMARY KEY,
        game_date DATE NOT NULL,
        home_team_id INTEGER NOT NULL REFERENCES teams(team_id),
        away_team_id INTEGER NOT NULL REFERENCES teams(team_id),
        home_score INTEGER,
        away_score INTEGER,
        status TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        player_id INTEGER PRIMARY KEY,
        full_name TEXT NOT NULL,
        team_id INTEGER REFERENCES teams(team_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS batting_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER NOT NULL REFERENCES games(game_id),
        player_id INTEGER NOT NULL REFERENCES players(player_id),
        at_bats INTEGER,
        hits INTEGER,
        home_runs INTEGER,
        rbi INTEGER,
        runs INTEGER,
        walks INTEGER,
        strikeouts INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pitching_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER NOT NULL REFERENCES games(game_id),
        player_id INTEGER NOT NULL REFERENCES players(player_id),
        innings_pitched REAL,
        hits_allowed INTEGER,
        runs_allowed INTEGER,
        earned_runs INTEGER,
        walks INTEGER,
        strikeouts INTEGER,
        decision TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER NOT NULL REFERENCES games(game_id),
        headline TEXT,
        body TEXT NOT NULL,
        generated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
    print("Database initialized!")

if __name__ == "__main__":
    init_db()
    