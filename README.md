# STRATA
S.T.R.A.T.A: System for Tracking, Reporting, and Analytical Tactical Assessment.

strata/
│
├── main.py            # Entry point; handles the interactive CLI loop, menu, and user commands.
├── database.py        # Handles SQLite connection, schema initialization, and data queries.
├── visualizer.py      # Manages NumPy calculations and Matplotlib radar│ chart rendering.
├── requirements.txt   # Lists project dependencies (matplotlib, numpy).
├── README.md          # Project documentation and usage instructions.
└── seed _ test _ data.py

# S.T.R.A.T.A.

### 🚀 S.T.R.A.T.A. Development Log

#### 📌 Current Status: Phase 1 Complete (Database & Visualizer Engine)

---

#### 🛠️ Completed Modules
* **`database.py`**
  * Established SQLite backend with schema support for `topics`, `sessions`, and `settings`.
  * Configured `max_weekly_hours` global weekly cap parameter.
  * Implemented mathematical boundary validation inside `update_topic_minimum()` to prevent user allocations from exceeding the global cap.
  * Configured query aggregators (`get_progress()`, `get_topics()`, `log_session()`) for visualizer integration.

* **`visualizer.py`**
  * Created an interactive Matplotlib radar visualizer styled in a dark cyberpunk theme (`#121212`).
  * Plotted the minimum required hours polygon ("Danger Zone") against actual logged study hours ("Actual Progress").
  * Centered layout explicitly and pinned a live `GLOBAL WEEKLY CAP` text label to the bottom of the canvas.
  * Fixed GUI event loop blocking to ensure native window toolbar responsiveness (zoom, pan, save) without desktop environment freezing.

* **`seed_test_data.py`**
  * Built a seed script to generate randomized study sessions across all database topics to verify visualizer polygon overlays.

---

#### 🎯 Next Immediate Action Item
* **Build `main.py`**: Implement the main terminal loop featuring the interactive **"Time Budget"** configuration menu, session logger interface, and visualizer popup trigger.
