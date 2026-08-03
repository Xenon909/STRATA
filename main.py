import sys
import os
from datetime import datetime, timedelta
import database as db
import visualizer

# Custom Command Prompt Prefix
PROMPT = "STRATA> "

def clear_screen():
    """Clears the terminal screen for a clean UI refresh."""
    os.system('clear')

def pause():
    """Holds the screen state so the user can read output before it clears."""
    input("\nPress Enter to return to Nexus...")

def print_header(title):
    """Clears screen and prints the section header."""
    clear_screen()
    print("\n" + "=" * 45)
    print(f" STRATA :: {title}")
    print("=" * 45)

def select_topic():
    """Helper function to cleanly list and select a topic from the database."""
    topics = db.get_topics()
    if not topics:
        print("[!] No topics available. Please configure your Time Budget first.")
        return None
    
    print("\nAvailable Topics:")
    for idx, (t_id, name, min_hours) in enumerate(topics):
        print(f"[{idx+1}] {name} (Min Req: {min_hours}h)")
    
    while True:
        choice = input(f"\nSelect Topic ID (or 0 to cancel)\n{PROMPT}").strip()
        if choice == '0':
            return None
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(topics):
                return topics[choice_idx][1]  # Return the string name of the topic
            print("[!] Invalid selection.")
        except ValueError:
            print("[!] Please enter a valid numerical ID.")

def select_preset():
    """Helper function to cleanly list and select a preset configuration."""
    presets = db.get_presets()
    if not presets:
        print("[!] No presets available.")
        return None
        
    print("\nAvailable Presets:")
    for idx, (p_id, name) in enumerate(presets):
        print(f"[{idx+1}] {name}")
        
    while True:
        choice = input(f"\nSelect Preset ID (or 0 to cancel)\n{PROMPT}").strip()
        if choice == '0':
            return None
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(presets):
                return presets[choice_idx][0]  # Return the preset ID
            print("[!] Invalid selection.")
        except ValueError:
            print("[!] Please enter a valid numerical ID.")

def handle_live_session():
    """Starts a live focus timer that strictly blocks out all other application features."""
    print_header("LIVE FOCUS SESSION")
    topic = select_topic()
    if not topic:
        return
    
    start_time = datetime.now()
    print(f"\n[ACTIVE] Session locked for '{topic}'.")
    print(f"[ACTIVE] Start time: {start_time.strftime('%H:%M:%S')}")
    print(">> Type exactly 'END' (case-sensitive) to stop the timer and log the session. <<\n")
    
    while True:
        cmd = input(PROMPT)
        if cmd == "END":
            end_time = datetime.now()
            break
        else:
            print("[!] Command ignored. Focus mode active. Type 'END' to terminate.")
    
    db.log_session(topic, start_time, end_time)
    duration = (end_time - start_time).total_seconds() / 60
    print(f"\n[SUCCESS] Logged {duration:.1f} minutes for '{topic}'.")
    pause()

def handle_afk_session():
    """Logs an asynchronous session using minimal input to synthesize exact timestamps."""
    print_header("AFK SESSION SYNC")
    topic = select_topic()
    if not topic:
        return
        
    # 1. Date Input & Parsing
    date_str = input(f"\nDate [Leave blank for Today, type 'yesterday', or YYYY-MM-DD]\n{PROMPT}").strip().lower()
    if date_str == '' or date_str == 'today':
        target_date = datetime.now().date()
    elif date_str == 'yesterday':
        target_date = (datetime.now() - timedelta(days=1)).date()
    else:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print("[!] Invalid date format. Aborting to avoid database corruption.")
            pause()
            return
            
    # 2. Start Time Input & Parsing
    time_str = input(f"\nStart Time (24h format, e.g., 14:30)\n{PROMPT}").strip()
    try:
        target_time = datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        print("[!] Invalid time format. Aborting.")
        pause()
        return
        
    # 3. Duration Input
    duration_str = input(f"\nDuration (in precise minutes)\n{PROMPT}").strip()
    try:
        duration_mins = int(duration_str)
    except ValueError:
        print("[!] Duration must be an integer. Aborting.")
        pause()
        return
        
    # Synthesize Timestamps
    start_time = datetime.combine(target_date, target_time)
    end_time = start_time + timedelta(minutes=duration_mins)
    
    db.log_session(topic, start_time, end_time)
    print(f"\n[SUCCESS] AFK Sync Complete: '{topic}' logged on {start_time.strftime('%Y-%m-%d')} for {duration_mins}m.")
    pause()

def handle_preset_manager():
    """Handles the sub-menu for applying, saving, and overwriting presets."""
    while True:
        print_header("PRESET MANAGER")
        print("[1] Apply a Preset (Overwrites current grid)")
        print("[2] Save Current Grid as New Preset")
        print("[3] Overwrite an Existing Preset (Snapshot current grid)")
        print("[0] Return to Time Budget Manager")
        
        choice = input(f"\n{PROMPT}").strip()
        
        if choice == '1':
            preset_id = select_preset()
            if preset_id:
                try:
                    db.apply_preset(preset_id)
                    print(f"\n[SUCCESS] Preset applied. Your operational grid has been updated.")
                except Exception as e:
                    print(f"\n[!] Validation Error: {e}")
            pause()
        elif choice == '2':
            name = input(f"\nEnter name for the new preset (e.g., Exam Centered)\n{PROMPT}").strip()
            if name:
                try:
                    db.save_new_preset(name)
                    print(f"\n[SUCCESS] Current grid snapshot saved as new preset: '{name}'.")
                except Exception as e:
                    print(f"\n[!] Error: {e}")
            pause()
        elif choice == '3':
            preset_id = select_preset()
            if preset_id:
                try:
                    db.overwrite_preset(preset_id)
                    print(f"\n[SUCCESS] Selected preset has been overwritten with your current grid snapshot.")
                except Exception as e:
                    print(f"\n[!] Error: {e}")
            pause()
        elif choice == '0':
            return
        else:
            print("\n[!] Unrecognized command.")
            pause()

def handle_time_budget():
    """Allows adjustments to global caps and specific topic minimums."""
    while True:
        print_header("TIME BUDGET MANAGER")
        print("[1] Modify Global Weekly Cap")
        print("[2] Modify Topic Danger Zone (Min Required Hours)")
        print("[3] Preset Manager (Apply / Save / Overwrite Sets)")
        print("[0] Return to Nexus")
        
        choice = input(f"\n{PROMPT}").strip()
        
        if choice == '1':
            new_cap = input(f"Enter new global cap in hours (e.g., 40.5)\n{PROMPT}").strip()
            try:
                db.update_global_cap(float(new_cap))
                print(f"\n[SUCCESS] Global weekly cap updated to {new_cap} hours.")
            except ValueError:
                print("\n[!] Invalid number format.")
            pause()
        elif choice == '2':
            topic = select_topic()
            if topic:
                new_min = input(f"Enter new minimum weekly hours for '{topic}'\n{PROMPT}").strip()
                try:
                    db.update_topic_minimum(topic, float(new_min))
                    print(f"\n[SUCCESS] Danger Zone for '{topic}' updated to {new_min} hours.")
                except Exception as e:
                    print(f"\n[!] Validation Error: {e}")
                pause()
        elif choice == '3':
            handle_preset_manager()
        elif choice == '0':
            return
        else:
            print("\n[!] Unrecognized command.")
            pause()

def main_loop():
    """Core execution loop for the STRATA CLI."""
    db.init_db()
    
    # Startup Safety Check
    total_allocated = db.get_total_allocated_hours()
    global_cap = db.get_global_cap()
    
    if total_allocated > global_cap:
        clear_screen()
        print("\n" + "!" * 45)
        print(" [WARNING] TIME BUDGET OVERDRAFT DETECTED")
        print("!" * 45)
        print(f"\nTotal allocated minimum hours: {total_allocated:.1f}h")
        print(f"Global weekly cap:             {global_cap:.1f}h")
        print(f"Deficit:                       {total_allocated - global_cap:.1f}h")
        print("\n[!] Your required topic minimums mathematically exceed your total available time.")
        print(">> Please navigate to [3] Manage Time Budget to resolve this conflict. <<")
        pause()
    
    while True:
        print_header("COMMAND NEXUS")
        print("[1] Live Focus Session")
        print("[2] View Operational Grid")
        print("[3] Manage Time Budget")
        print("[4] AFK Session Sync")
        print("[0] Exit System")
        
        choice = input(f"\n{PROMPT}").strip()
        
        if choice == '1':
            handle_live_session()
        elif choice == '2':
            print("\n[STRATA] Launching Visualizer Canvas...")
            visualizer.render_radar_chart()
        elif choice == '3':
            handle_time_budget()
        elif choice == '4':
            handle_afk_session()
        elif choice == '0':
            clear_screen()
            print("\n[STRATA] Terminating system. Goodbye.\n")
            sys.exit(0)
        else:
            print("\n[!] Unrecognized command. Please enter a valid numerical ID.")
            pause()

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        clear_screen()
        print("\n\n[!] System interrupt detected. Safely terminating STRATA...\n")
        sys.exit(0)
