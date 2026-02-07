from datetime import datetime
import sqlite3

DATABASE = "welcome_window.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS availability (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT NOT NULL DEFAULT 'away',
            message TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visitor_name TEXT,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visitor_name TEXT,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP,
            connection_type TEXT,
            duration_seconds INTEGER
        )
    """)

    cursor.execute("SELECT COUNT(*) as count FROM availability")
    if cursor.fetchone()["count"] == 0:
        cursor.execute(
            "INSERT INTO availability (status, message) VALUES ('away', 'Not available right now')"
        )

    conn.commit()
    conn.close()


def get_current_status():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM availability ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "status": result["status"],
            "message": result["message"],
            "updated_at": result["updated_at"],
        }
    return {"status": "away", "message": "Not available", "updated_at": None}


def update_status(status, message):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO availability (status, message) VALUES (?, ?)", (status, message)
    )
    conn.commit()
    conn.close()


def add_message(visitor_name, message):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (visitor_name, message) VALUES (?, ?)",
        (visitor_name, message),
    )
    conn.commit()
    conn.close()


def get_messages(limit=50, unread_only=False):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM messages"
    if unread_only:
        query += " WHERE is_read = 0"
    query += " ORDER BY created_at DESC LIMIT ?"
    cursor.execute(query, (limit,))
    messages = cursor.fetchall()
    conn.close()
    return [dict(msg) for msg in messages]


def mark_message_read(message_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE messages SET is_read = 1 WHERE id = ?", (message_id,))
    conn.commit()
    conn.close()


def get_unread_count():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM messages WHERE is_read = 0")
    result = cursor.fetchone()
    conn.close()
    return result["count"]


def log_visit(visitor_name, connection_type):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO visits (visitor_name, connection_type) VALUES (?, ?)",
        (visitor_name, connection_type),
    )
    visit_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return visit_id


def end_visit(visit_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE visits 
        SET ended_at = CURRENT_TIMESTAMP,
            duration_seconds = (strftime('%s', CURRENT_TIMESTAMP) - strftime('%s', started_at))
        WHERE id = ?
    """,
        (visit_id,),
    )
    conn.commit()
    conn.close()


def get_recent_visits(limit=20):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM visits ORDER BY started_at DESC LIMIT ?", (limit,))
    visits = cursor.fetchall()
    conn.close()
    return [dict(visit) for visit in visits]


def get_visit_stats():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM visits")
    total = cursor.fetchone()["total"]
    cursor.execute(
        "SELECT COUNT(*) as today FROM visits WHERE DATE(started_at) = DATE('now')"
    )
    today = cursor.fetchone()["today"]
    cursor.execute(
        "SELECT AVG(duration_seconds) as avg_duration FROM visits WHERE duration_seconds IS NOT NULL"
    )
    avg_duration = cursor.fetchone()["avg_duration"] or 0
    conn.close()
    return {
        "total_visits": total,
        "today_visits": today,
        "avg_duration_minutes": round(avg_duration / 60, 1) if avg_duration else 0,
    }
