import sqlite3

DATABASE = 'sqlite/tollugatti.db'

def execute_query(query, params=()):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor

def create_user(username, password):
    query = 'INSERT INTO Users (username, password) VALUES (?, ?)'
    execute_query(query, (username, password))

def authenticate_user(username, password):
    query = 'SELECT id FROM Users WHERE username = ? AND password = ?'
    cursor = execute_query(query, (username, password))
    return cursor.fetchone() is not None

def save_game(user_id, game_name, mode, players):
    query = 'INSERT INTO Games (game_name, mode, players) VALUES (?, ?, ?)'
    cursor = execute_query(query, (game_name, mode, players))
    game_id = cursor.lastrowid
    
    query = 'INSERT INTO UserGames (user_id, game_id) VALUES (?, ?)'
    execute_query(query, (user_id, game_id))

def get_user_games(user_id):
    query = '''SELECT Games.game_name, Games.mode, Games.players
               FROM UserGames
               JOIN Games ON UserGames.game_id = Games.id
               WHERE UserGames.user_id = ?'''
    cursor = execute_query(query, (user_id,))
    return cursor.fetchall()
