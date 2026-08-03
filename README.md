# STRATA
> S.T.R.A.T.A: System for Tracking, Reporting, and Analytical Tactical Assessment.
> A terminal-based study tracker and time-budgeting tool.

## Overview

STRATA was originally engineered to manage the rigorous, high-volume academic study blocks required for CPGE (MPSI / MP) coursework. However, its core architecture makes it a versatile, **all-purpose study tracker** for anyone needing strict time-budgeting and topic progression tracking.

At its core, STRATA monitors your weekly progress by topic using an integrated **radar chart visualizer**, allowing you to instantly gauge whether your time distribution aligns with your academic goals.

## Key Features

*   **Radar Chart Visualizer:** Track weekly progress across multiple subjects visually directly in the terminal, ensuring balanced time allocation.
*   **Global Weekly Time-Cap:** A built-in safety mechanism that enforces study boundaries to prevent burnout and strictly limit over-exertion.
*   **Preset Management System:** Seamlessly swap between different academic schedules, intensive sprint focuses, or term modules.
*   **Local & Lightweight:** Powered by a native Python backend and an SQLite database for fast, persistent session logging.
*   **TUI Optimized:** Designed for a terminal workflow, specifically tailored for seamless integration alongside Emacs.

### 1. Installation & Dependencies

It is recommended to install dependencies via system-level package managers to ensure native event loop stability and avoid GUI window freezes.

On Debian / Ubuntu:
```bash
sudo apt update
sudo apt install python3 python3-matplotlib sqlite3
```

### 2. Architecture & Method of Usage

STRATA operates through a clear command prompt (STRATA> ) separated into five core directives:

=============================================
 S.T.R.A.T.A. :: COMMAND NEXUS
=============================================
[1] Live Focus Session
[2] View Operational Grid
[3] Manage Time Budget
[4] AFK Session Sync
[0] Exit System


#### [1] Live Focus Session

    Select your target study module (e.g., Maths, Physics).

    The system locks the terminal into an active study state. All menu options and visualizers are inaccessible during an active block.

    To exit and log the precise time delta to the database, type END (case-sensitive). Accidental keystrokes or inputs are ignored.

#### [2] View Operational Grid (Radar Visualizer)

    Generates a Cyberpunk dark-mode radar plot rendering your actual logged 7-day trailing hours against your required "Danger Zone" minimums.

    Outer boundaries are dynamically anchored to your Global Cap, maintaining exact visual proportions week-over-week.

    Executes in blocking GUI mode (plt.show()) to ensure terminal safety and responsive window management.

#### [3] Manage Time Budget & Presets

    Modify Global Weekly Cap: Adjust the total hard ceiling of study hours available per week.

    Modify Topic Danger Zone: Adjust individual minimum weekly thresholds per topic. Includes smart validation to prevent overdrafting the global cap.

    Preset Manager:

        Apply Preset: Load premade allocations (e.g., Normal Prepa Week).

        Save New Preset: Snapshot your current active allocations into a reusable preset.

        Overwrite Preset: Update existing presets directly from your live grid setup.

#### [4] AFK Session Sync

For sessions completed away from your workstation (co-working spaces, library, classes):

    Date: Accepts blank (defaults to today), yesterday, or explicit YYYY-MM-DD.

    Start Time: Accepts simple 24h format (e.g., 14:30).

    Duration: Input precise length in minutes (e.g., 120).

STRATA automatically synthesizes exact start and end timestamps into SQLite to maintain long-term chronotype performance analytics.
