import sqlite3
from datetime import datetime
import os

DB_FILE = 'strata_data.db'

def get_connection():
    """Establishes and returns a connection to the SQLite database."""
    return sqlite3.connect(DB_FILE)

def init_db():
    """Initializes the database schema and seeds default structure."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create topics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            min_hours REAL NOT NULL
        )
    """)
    
    # Create sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            duration_minutes REAL,
            FOREIGN KEY(topic_id) REFERENCES topics(id)
        )
    """)

    # Create settings table for global configurations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value REAL NOT NULL
        )
    """)
    
    # Seed default maximum weekly hours if not set (baseline 40 hours)
    cursor.execute("SELECT COUNT(*) FROM settings WHERE key = 'max_weekly_hours'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO settings (key, value) VALUES ('max_weekly_hours', 40.0)")

    # Seed default topics if none exist to establish baseline
    cursor.execute("SELECT COUNT(*) FROM topics")
    if cursor.fetchone()[0] == 0:
        default_topics = [
            ("Maths", 14.0),
            ("Physics", 12.0),
            ("Info", 6.0),
            ("French", 4.0),            
            ("SI", 4.0),
            ("Chemistry", 12.0),
            ("TIPE", 1.0),
            ("Trad", 0.5),
            ("English", 0.3)            
        ]
        cursor.executemany("INSERT INTO topics (name, min_hours) VALUES (?, ?)", default_topics)
        
    conn.commit()
    conn.close()

def get_global_cap():
    """Retrieves the maximum weekly study hours cap."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'max_weekly_hours'")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0.0

def update_global_cap(new_cap):
    """Updates the maximum weekly study hours cap."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE settings SET value = ? WHERE key = 'max_weekly_hours'", (new_cap,))
    conn.commit()
    conn.close()

def get_total_allocated_hours():
    """Returns the sum of all minimum hours currently allocated across topics."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(SUM(min_hours), 0) FROM topics")
    result = cursor.fetchone()
    conn.close()
    return result[0]

def get_topics():
    """Returns a list of all topics."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, min_hours FROM topics")
    topics = cursor.fetchall()
    conn.close()
    return topics

def update_topic_minimum(topic_id, new_hours):
    """Updates the minimum hours for a specific topic, enforcing the global cap limit."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get current hours for this specific topic
    cursor.execute("SELECT min_hours FROM topics WHERE id = ?", (topic_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        raise ValueError("Topic not found.")
        
    current_topic_hours = result[0]
    
    # Calculate new total against the cap
    total_allocated = get_total_allocated_hours()
    global_cap = get_global_cap()
    
    projected_total = (total_allocated - current_topic_hours) + new_hours
    
    if projected_total > global_cap:
        conn.close()
        raise ValueError(f"Update rejected: Exceeds weekly cap of {global_cap} hours by {projected_total - global_cap} hours.")
        
    cursor.execute("UPDATE topics SET min_hours = ? WHERE id = ?", (new_hours, topic_id))
    conn.commit()
    conn.close()

def log_session(topic_name, start_time, end_time):
    """Logs a study session and calculates duration."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM topics WHERE name = ?", (topic_name,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        raise ValueError(f"Topic '{topic_name}' not found in the tracking grid.")
        
    topic_id = result[0]
    duration_minutes = (end_time - start_time).total_seconds() / 60.0
    
    cursor.execute("""
        INSERT INTO sessions (topic_id, start_time, end_time, duration_minutes)
        VALUES (?, ?, ?, ?)
    """, (topic_id, start_time, end_time, duration_minutes))
    
    conn.commit()
    conn.close()
    return duration_minutes

def get_progress():
    """Aggregates logged hours against minimum threshold parameters for the visualizer."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT t.name, t.min_hours, COALESCE(SUM(s.duration_minutes) / 60.0, 0) as logged_hours
        FROM topics t
        LEFT JOIN sessions s ON t.id = s.topic_id
        GROUP BY t.id
    """)
    
    progress = cursor.fetchall()
    conn.close()
    return progress

if __name__ == "__main__":
    init_db()
