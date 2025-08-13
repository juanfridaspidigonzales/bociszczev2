import sqlite3

DB_FILE = "chat_history.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Dane postaci
    c.execute("""
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """)
    # Nauczone zaklęcia
    c.execute("""
        CREATE TABLE IF NOT EXISTS spells (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            spell_name TEXT NOT NULL,
            learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, spell_name)
        )
    """)
    conn.commit()
    conn.close()

def create_or_update_character(user_id, name, description):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO characters (user_id, name, description)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            name=excluded.name,
            description=excluded.description
    """, (user_id, name, description))
    conn.commit()
    conn.close()
    
# Pobiera dane postaci dla danego user_id
def get_character(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT id, name, description FROM characters
        WHERE user_id = ? LIMIT 1
    """, (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "description": row[2]}
    return None

# Dodaje zaklęcie do postaci (jeśli nie było wcześniej dodane)
def add_spell_to_character(user_id, spell_name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT OR IGNORE INTO spells (user_id, spell_name)
        VALUES (?, ?)
    """, (user_id, spell_name))
    conn.commit()
    conn.close()

# Zwraca listę (zaklęcie, liczba_treningów) dla danego użytkownika.
def get_spell_training_counts(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT spell_name, COUNT(*) as trainings_count
        FROM spells
        WHERE user_id = ?
        GROUP BY spell_name
        ORDER BY trainings_count DESC
    """, (user_id,))
    data = c.fetchall()
    conn.close()
    return data
