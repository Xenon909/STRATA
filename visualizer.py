import matplotlib.pyplot as plt
import numpy as np
import database as db

def render_radar_chart():
    """
    Renders a blocking, interactive radar chart in a dark cyberpunk style.
    Maps current logged study hours against the minimum 'Danger Zone' threshold.
    """
    # Apply dark background preset
    plt.style.use('dark_background')
    
    # Fetch data from SQLite database
    progress_data = db.get_progress()
    global_cap = db.get_global_cap()
    
    if not progress_data:
        print("[S.T.R.A.T.A.] No topics found in database to render.")
        return

    # Extract topic names, min required hours, and actual logged hours
    topics = [row[0] for row in progress_data]
    min_hours = [row[1] for row in progress_data]
    logged_hours = [row[2] for row in progress_data]
    
    num_vars = len(topics)
    if num_vars < 3:
        print("[S.T.R.A.T.A.] Warning: Radar charts require at least 3 topics to display properly.")
        return

    # Calculate angles for each topic axis
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # Complete the loop to close the radar polygons
    topics_closed = topics + [topics[0]]
    min_hours_closed = min_hours + [min_hours[0]]
    logged_hours_closed = logged_hours + [logged_hours[0]]
    angles_closed = angles + [angles[0]]

    # Setup figure with dark cyberpunk background (#121212)
    # Increased width slightly to give the legend breathing room without shifting the circle
    fig, ax = plt.subplots(figsize=(8, 7), subplot_kw=dict(polar=True), facecolor='#121212')
    ax.set_facecolor('#121212')

    # Radial Axis Max Limit (Global Cap Scale):
    # Set maximum limit based on highest allocation or a portion of total global cap + buffer
    max_threshold = max(max(min_hours_closed), max(logged_hours_closed), global_cap / 2.5)
    ax.set_ylim(0, max_threshold + 2.0)

    # Styling polar grid and ticks
    ax.set_theta_offset(np.pi / 2)  # Top center (12 o'clock position)
    ax.set_theta_direction(-1)     # Clockwise direction
    
    ax.set_xticks(angles)
    ax.set_xticklabels(topics, color='#e0e0e0', fontsize=10, fontweight='bold')
    
    ax.tick_params(colors='#888888')
    ax.grid(color='#333333', linestyle='--', linewidth=0.8)
    ax.spines['polar'].set_color('#444444')

    # 1. Plot Danger Zone Polygon (Neon Red)
    ax.plot(angles_closed, min_hours_closed, color='#ff3366', linewidth=2, linestyle='--', label='Danger Zone (Min Req)')
    ax.fill(angles_closed, min_hours_closed, color='#ff3366', alpha=0.25)

    # 2. Plot Actual Progress Polygon (Neon Cyan)
    ax.plot(angles_closed, logged_hours_closed, color='#00f3ff', linewidth=2.5, label='Actual Progress')
    ax.fill(angles_closed, logged_hours_closed, color='#00f3ff', alpha=0.35)

    # Title Configuration
    plt.title("S.T.R.A.T.A. :: Operational Grid", color='#ffffff', fontsize=14, pad=35, fontweight='bold')
    
    # Legend Configuration
    legend = plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1.1), facecolor='#1e1e1e', edgecolor='#444444')
    for text in legend.get_texts():
        text.set_color("#ffffff")

    # Replaced tight_layout with manual centering
    # This prevents the legend from pushing the radar circle to the left
    plt.subplots_adjust(left=0.15, right=0.85, top=0.80, bottom=0.15)
    
    # Global Weekly Cap Text placed at the absolute bottom center
    plt.figtext(0.5, 0.05, f"GLOBAL WEEKLY CAP: {global_cap:.1f} HOURS", ha='center', va='center', color='#888888', fontsize=11, fontweight='bold')

    # GUI Blocking Mode: Hands control over to the Matplotlib event loop
    plt.show()

if __name__ == "__main__":
    db.init_db()
    render_radar_chart()


