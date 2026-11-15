
import sqlite3

DATABASE_NAME = "ecosched.db"


# Create Database and Tables

def create_database():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    # Store simulation details

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS simulation_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            algorithm TEXT,
            power_mode TEXT,
            quantum INTEGER,
            total_energy REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Store individual process results

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS simulation_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            pid TEXT,
            arrival_time REAL,
            burst_time REAL,
            priority INTEGER,
            execution_time REAL,
            selected_power_mode TEXT,
            completion_time REAL,
            turnaround_time REAL,
            waiting_time REAL,
            energy_used REAL,
            FOREIGN KEY (run_id) REFERENCES simulation_runs(id)
        )
    """)

    connection.commit()
    connection.close()


# Save Simulation Results

def save_simulation(algorithm, power_mode, quantum, total_energy, processes, results):

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO simulation_runs
        (algorithm, power_mode, quantum, total_energy)
        VALUES (?, ?, ?, ?)
    """, (algorithm, power_mode, quantum, total_energy))

    run_id = cursor.lastrowid

    for i in range(len(results)):

        result = results[i]

        pid = result[0]

        arrival_time = result[1]
        burst_time = result[2]

        priority = 0

        for j in range(len(processes)):

            if processes[j]["pid"] == pid:
                priority = processes[j]["priority"]
                break

        if algorithm == "EcoSched":

            selected_power_mode = result[3]
            execution_time = result[4]
            completion_time = result[5]
            turnaround_time = result[6]
            waiting_time = result[7]
            energy_used = result[8]

        else:

            selected_power_mode = power_mode
            execution_time = burst_time
            completion_time = result[3]
            turnaround_time = result[4]
            waiting_time = result[5]

            energy_used = 0

            if power_mode == "Low":
                energy_used = burst_time * 4

            elif power_mode == "Medium":
                energy_used = burst_time * 5

            elif power_mode == "High":
                energy_used = burst_time * 6

        cursor.execute("""
            INSERT INTO simulation_results
            (
                run_id,
                pid,
                arrival_time,
                burst_time,
                priority,
                execution_time,
                selected_power_mode,
                completion_time,
                turnaround_time,
                waiting_time,
                energy_used
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id,
            pid,
            arrival_time,
            burst_time,
            priority,
            execution_time,
            selected_power_mode,
            completion_time,
            turnaround_time,
            waiting_time,
            energy_used
        ))

    connection.commit()
    connection.close()

    return run_id


# Get Simulation History

def get_history():

    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM simulation_runs
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    history = []

    for row in rows:
        history.append(dict(row))

    connection.close()

    return history


# Get Individual Process Results of a Simulation

def get_simulation_details(run_id):

    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM simulation_results
        WHERE run_id = ?
    """, (run_id,))

    rows = cursor.fetchall()

    details = []

    for row in rows:
        details.append(dict(row))

    connection.close()

    return details


if __name__ == "__main__":
    create_database()
    print("Database created successfully!")
