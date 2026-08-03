import database as db
from datetime import datetime, timedelta
import random

def seed_data():
    """Injects randomized dummy study sessions into the database for testing."""
    print("[S.T.R.A.T.A.] Initializing database structure...")
    db.init_db()
    
    topics = db.get_topics()
    if not topics:
        print("[S.T.R.A.T.A.] Error: No topics found. Ensure database initialized correctly.")
        return
        
    print(f"[S.T.R.A.T.A.] Found {len(topics)} topics. Injecting dummy logs...")
    now = datetime.now()
    
    # Track total injected hours for a quick summary
    total_injected_hours = 0
    
    for topic in topics:
        topic_id, topic_name, min_hours = topic
        
        # Generate between 2 and 5 random sessions per topic to create varied progress lines
        num_sessions = random.randint(2, 5)
        
        for _ in range(num_sessions):
            # Random duration between 45 minutes and 3.5 hours
            duration_minutes = random.randint(45, 210)
            
            # Random start time within the last 7 days
            days_ago = random.randint(0, 6)
            hours_ago = random.randint(0, 23)
            
            start_time = now - timedelta(days=days_ago, hours=hours_ago)
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            # Use the existing log_session function to ensure it formats perfectly
            db.log_session(topic_name, start_time, end_time)
            total_injected_hours += (duration_minutes / 60.0)
            
    print(f"[S.T.R.A.T.A.] Success! Injected {total_injected_hours:.1f} total hours of dummy data.")
    print("[S.T.R.A.T.A.] Run 'python3 visualizer.py' to view the progress overlay.")

if __name__ == "__main__":
    seed_data()
