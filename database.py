import sqlite3

DATABASE = 'ai_start_map.db'

def get_db():
    """Verbindung zur Datenbank öffnen"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Ergebnisse als Dictionary lesen
    return conn