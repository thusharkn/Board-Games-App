import sqlite3

def initialize_db():
    conn = sqlite3.connect('sqlite/tollugatti.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_name TEXT NOT NULL,
        mode TEXT NOT NULL,
        players INTEGER NOT NULL,
        username TEXT NOT NULL  -- Add this line to include the username column
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS UserGames (
        user_id INTEGER,
        game_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES Users (id),
        FOREIGN KEY (game_id) REFERENCES Games (id),
        PRIMARY KEY (user_id, game_id)
    )''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_db()
