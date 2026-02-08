from datetime import datetime
import sqlite3

DATABASE = "welcome_window.db"


def get_db():
    conn = sqlite3.connect(DATABASE, timeout=10)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for better concurrent access
    conn.execute("PRAGMA journal_mode=WAL")
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pending_visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved BOOLEAN DEFAULT 0,
            rejected BOOLEAN DEFAULT 0,
            approved_at TIMESTAMP,
            session_id TEXT UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            sender_name TEXT NOT NULL,
            message TEXT NOT NULL,
            visitor_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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


# New functions for visitor approval system
def create_pending_visitor(name, email, session_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pending_visitors (name, email, session_id) VALUES (?, ?, ?)",
        (name, email, session_id),
    )
    visitor_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return visitor_id


def get_pending_visitors():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM pending_visitors WHERE approved = 0 AND rejected = 0 ORDER BY requested_at DESC"
    )
    visitors = cursor.fetchall()
    conn.close()
    return [dict(v) for v in visitors]


def approve_visitor(visitor_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE pending_visitors SET approved = 1, approved_at = CURRENT_TIMESTAMP WHERE id = ?",
        (visitor_id,),
    )
    conn.commit()
    conn.close()


def reject_visitor(visitor_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE pending_visitors SET rejected = 1 WHERE id = ?",
        (visitor_id,),
    )
    conn.commit()
    conn.close()


def get_visitor_by_session(session_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM pending_visitors WHERE session_id = ?",
        (session_id,),
    )
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None


# Chat message persistence functions
def save_chat_message(sender, sender_name, message, visitor_id=None):
    """Save a chat message to database"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO chat_messages (sender, sender_name, message, visitor_id) 
           VALUES (?, ?, ?, ?)""",
        (sender, sender_name, message, visitor_id),
    )
    message_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return message_id


def get_chat_messages(limit=100):
    """Get recent chat messages"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT * FROM chat_messages 
           ORDER BY created_at ASC 
           LIMIT ?""",
        (limit,),
    )
    messages = cursor.fetchall()
    conn.close()
    return [dict(msg) for msg in messages]


def delete_chat_message(message_id):
    """Delete a specific chat message"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_messages WHERE id = ?", (message_id,))
    conn.commit()
    conn.close()


def clear_all_chat_messages():
    """Clear all chat messages"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_messages")
    conn.commit()
    conn.close()
