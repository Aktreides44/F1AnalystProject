# 🏎️ F1 Race Analysis – 2024 Italian Grand Prix

![Formula 1](https://upload.wikimedia.org/wikipedia/en/thumb/3/3b/Formula_1_Logo.svg/1200px-Formula_1_Logo.svg.png)

## Overview

This project builds a **relational MySQL database** and a **Python analysis pipeline** to evaluate Formula 1 driver performance for a single race session.

Key analyses include:

- **Lap Time Progression:** Track lap-to-lap pace and identify trends.
- **Sector Analysis:** Determine which sector contributes most to driver differences.
- **Telemetry Correlation:** Explore how speed, throttle, brake, and gear affect lap times.
- **Consistency Metrics:** Identify the most consistent drivers.
- **Combined Performance:** Aggregate multi-dimensional insights for overall driver performance.

---


---

## Database Design

### Tables

1. **sessions**
   - `session_id` (PK, INT, AUTO_INCREMENT)
   - `year`
   - `grand_prix`
   - `session_type`
   - `date`

2. **drivers**
   - `driver_id` (PK, INT, AUTO_INCREMENT)
   - `driver_number`
   - `abbreviation`
   - `full_name`

3. **laps**
   - `session_id` (FK)
   - `driver_id` (FK)
   - `lap_number`
   - `lap_time`, `sector1_time`, `sector2_time`, `sector3_time`
   - `pit`, `tyre_compound`, `stint_number`, `track_status`
   - **Primary Key:** `(session_id, driver_id, lap_number)`

4. **telemetry**
   - `session_id`, `driver_id`, `lap_number`, `sample_index` (PK composite)
   - `time`, `distance`, `speed`, `throttle`, `brake`, `gear`, `drs`, `rpm`
   - References `laps` table

---

## Setup Instructions

1. **Instal Python dependencies**
   [pip install fastf1 pandas matplotlib seaborn mysql-connector-python]

2. **Configure MySQL database**
   
   CREATE DATABASE f1_db;
   CREATE USER 'f1_user'@'localhost' IDENTIFIED BY 'yourpassword';
   GRANT ALL PRIVILEGES ON f1_db.* TO 'f1_user'@'localhost';
   FLUSH PRIVILEGES;

3. **Run the data insertion scripts**
   
   python Database/insert_sessions.py
   python Database/insert_drivers.py
   python Database/insert_laps.py
   python Database/insert_telemetry.py
   
5. **Run analysis scripts**


   python Analysis/lap_time_progression.py
   python Analysis/sector_time_comparison.py
   python Analysis/telemetry_correlation.py
   python Analysis/lap_consistency.py
   python Analysis/combined_performance.py

   

  

