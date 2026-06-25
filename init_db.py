import sqlite3


def init_db():
    # Verbindung zur DB, wird automatisch erstellt, wenn sie noch nicht existiert
    conn = sqlite3.connect("ai_start_map.db")

    # schema.sql lesen und ausführen
    with open("database/schema.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    conn.commit()
    conn.close()

    print("✅ Datenbank erfolgreich erstellt: ai_start_map.db")


if __name__ == "__main__":
    init_db()