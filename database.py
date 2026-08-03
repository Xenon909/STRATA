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
    
    # Create presets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS presets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)
    
    # Create preset_allocations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preset_allocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            preset_id INTEGER,
            topic_name TEXT,
            min_hours REAL,
            FOREIGN KEY(preset_id) REFERENCES presets(id)
        )
    """)
    
    # Seed default maximum weekly hours if not set (baseline 40 hours)
    cursor.execute("SELECT COUNT(*) FROM settings WHERE key = 'max_weekly_hours'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO settings (key, value) VALUES ('max_weekly_hours', 40.0)")

    # Baseline 40.0 hour distribution for a "Normal Prepa Week"
    default_topics = [
        ("Maths", 12.0),
        ("Physics", 10.0),
        ("Info", 4.0),
        ("SI", 4.0),
        ("Chemistry", 4.0),
        ("French", 2.0),
        ("English", 2.0),
        ("TIPE", 2.0),
        ("Trad", 0.0)
    ]

    # Seed default topics if none exist to establish baseline
    cursor.execute("SELECT COUNT(*) FROM topics")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO topics (name, min_hours) VALUES (?, ?)", default_topics)

    # Seed the default preset if no presets exist
    cursor.execute("SELECT COUNT(*) FROM presets")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO presets (name) VALUES ('Normal Prepa Week')")
        preset_id = cursor.lastrowid
        preset_data = [(preset_id, name, min_h) for name, min_h in default_topics]
        cursor.executemany("INSERT INTO preset_allocations (preset_id, topic_name, min_hours) VALUES (?, ?, ?)", preset_data)
        
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

def update_topic_minimum(topic_name, new_hours):
    """Updates the minimum hours for a specific topic, intelligently enforcing cap logic."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT min_hours FROM topics WHERE name = ?", (topic_name,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        raise ValueError(f"Topic '{topic_name}' not found.")
        
    current_topic_hours = result[0]
    
    total_allocated = get_total_allocated_hours()
    global_cap = get_global_cap()
    
    projected_total = (total_allocated - current_topic_hours) + new_hours
    
    # Catch-22 Fix: Only block the update if they exceed the cap AND are trying to increase the hours
    if projected_total > global_cap and new_hours > current_topic_hours:
        conn.close()
        raise ValueError(f"Update rejected: Exceeds weekly cap of {global_cap} hours by {projected_total - global_cap:.1f} hours.")
        
    cursor.execute("UPDATE topics SET min_hours = ? WHERE name = ?", (new_hours, topic_name))
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

# ==========================================
# PRESET MANAGEMENT FUNCTIONS
# ==========================================

def get_presets():
    """Fetches all saved configuration presets."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM presets ORDER BY id ASC")
    presets = cursor.fetchall()
    conn.close()
    return presets

def apply_preset(preset_id):
    """Overwrites current live grid with a preset's allocations."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Calculate the total hours of the requested preset
    cursor.execute("SELECT COALESCE(SUM(min_hours), 0) FROM preset_allocations WHERE preset_id = ?", (preset_id,))
    preset_total = cursor.fetchone()[0]
    global_cap = get_global_cap()
    
    if preset_total > global_cap:
        conn.close()
        raise ValueError(f"Cannot apply preset: Total hours ({preset_total:.1f}h) mathematically exceeds your current Global Cap ({global_cap:.1f}h).")
        
    # Apply to topics
    cursor.execute("SELECT topic_name, min_hours FROM preset_allocations WHERE preset_id = ?", (preset_id,))
    allocations = cursor.fetchall()
    
    for topic_name, min_hours in allocations:
        cursor.execute("UPDATE topics SET min_hours = ? WHERE name = ?", (min_hours, topic_name))
        
    conn.commit()
    conn.close()

def save_new_preset(preset_name):
    """Takes a snapshot of current allocations and saves them as a new preset."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO presets (name) VALUES (?)", (preset_name,))
        preset_id = cursor.lastrowid
        
        cursor.execute("SELECT name, min_hours FROM topics")
        current_topics = cursor.fetchall()
        
        allocations = [(preset_id, t[0], t[1]) for t in current_topics]
        cursor.executemany("INSERT INTO preset_allocations (preset_id, topic_name, min_hours) VALUES (?, ?, ?)", allocations)
        
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError(f"Preset name '{preset_name}' already exists.")
        
    conn.close()

def overwrite_preset(preset_id):
    """Deletes old preset allocations and overwrites them with a fresh snapshot of the current grid."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Clear out old allocations
    cursor.execute("DELETE FROM preset_allocations WHERE preset_id = ?", (preset_id,))
    
    # Capture fresh snapshot
    cursor.execute("SELECT name, min_hours FROM topics")
    current_topics = cursor.fetchall()
    
    allocations = [(preset_id, t[0], t[1]) for t in current_topics]
    cursor.executemany("INSERT INTO preset_allocations (preset_id, topic_name, min_hours) VALUES (?, ?, ?)", allocations)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
