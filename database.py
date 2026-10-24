import sqlite3

DB_NAME = "sentiment.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # History table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT NOT NULL,
            platform TEXT NOT NULL,
            content TEXT,
            image TEXT,
            sentiment TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def register_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def validate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, username FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cursor.fetchone()
    conn.close()
    return user


def add_history(time, platform, content, image, sentiment):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO history (time, platform, content, image, sentiment)
        VALUES (?, ?, ?, ?, ?)
    """, (time, platform, content, image, sentiment))

    conn.commit()
    conn.close()


def get_history():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT time, platform, content, image, sentiment
        FROM history
        ORDER BY id DESC
    """)

    data = cursor.fetchall()
    conn.close()
    return data