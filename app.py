
from flask import Flask, render_template, request, jsonify
import math

from scheduler import (
    fcfs,
    sjf,
    priority_scheduling,
    round_robin,
    ecosched
)

from energy_calculator import calculate_energy

from database import (
    create_database,
    save_simulation,
    get_history,
    get_simulation_details
)

from system_monitor import get_system_metrics


app = Flask(__name__)

# Create Database
create_database()


# Validate Numeric Values

def valid_number(value):

    if isinstance(value, bool):
        return False

    try:
        number = float(value)

        return math.isfinite(number)

    except (ValueError, TypeError, OverflowError):

        return False


# Validate Process Data

def validate_processes(processes):

    if not isinstance(processes, list):

        return None, "Processes must be provided as a list"

    if len(processes) == 0:

        return None, "Please add at least one process"

    validated_processes = []
    used_pids = set()

    for index, process in enumerate(processes):

        if not isinstance(process, dict):

            return None, "Each process must be an object"

        required_fields = [
            "pid",
            "arrival_time",
            "burst_time",
            "priority"
        ]

        for field in required_fields:

            if field not in process:

                return None, (
                    "Missing " + field +
                    " in process " + str(index + 1)
                )

        pid = process["pid"]

        if not isinstance(pid, str) or not pid.strip():

            return None, "Process ID cannot be empty"

        pid = pid.strip()

        if pid in used_pids:

            return None, "Duplicate process ID: " + pid

        used_pids.add(pid)

        arrival = process["arrival_time"]
        burst = process["burst_time"]
        priority = process["priority"]

        if not valid_number(arrival):

            return None, "Invalid arrival time for " + pid

        if not valid_number(burst):

            return None, "Invalid burst time for " + pid

        if not valid_number(priority):

            return None, "Invalid priority for " + pid

        arrival = float(arrival)
        burst = float(burst)
        priority = float(priority)

        if arrival < 0:

            return None, "Arrival time cannot be negative"

        if burst <= 0:

            return None, "Burst time must be greater than zero"

        if priority < 1 or not priority.is_integer():

            return None, "Priority must be a positive integer"

        # Keep other process fields, if any

        new_process = process.copy()

        new_process["pid"] = pid
        new_process["arrival_time"] = arrival
        new_process["burst_time"] = burst
        new_process["priority"] = int(priority)

        validated_processes.append(new_process)

    return validated_processes, None


# Validate Power Mode

def validate_power_mode(power_mode):

    return power_mode in ["Low", "Medium", "High"]


# Validate Quantum

def validate_quantum(quantum):

    if not valid_number(quantum):

        return False

    quantum = float(quantum)

    return quantum > 0


# Read and Validate JSON Data

def get_request_data():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):

        return None, "Invalid or missing JSON request"

    return data, None


# Home Page

@app.route("/")
def home():

    return render_template("index.html")


# Run Selected Algorithm

@app.route("/run", methods=["POST"])
def run_simulation():

    data, error = get_request_data()

    if error:

        return jsonify({"error": error}), 400

    processes, error = validate_processes(
        data.get("processes")
    )

    if error:

        return jsonify({"error": error}), 400

    algorithm = data.get("algorithm")

    if not isinstance(algorithm, str):

        return jsonify({"error": "Invalid algorithm"}), 400

    power_mode = data.get("power_mode")

    if not validate_power_mode(power_mode):

        return jsonify({"error": "Invalid power mode"}), 400

    quantum = data.get("quantum", 2)

    if algorithm not in [
        "FCFS",
        "SJF",
        "Priority",
        "Round Robin",
        "EcoSched"
    ]:

        return jsonify({
            "error": "Invalid scheduling algorithm"
        }), 400

    if algorithm == "Round Robin":

        if not validate_quantum(quantum):

            return jsonify({
                "error": "Time quantum must be positive"
            }), 400

        quantum = float(quantum)

    # FCFS

    if algorithm == "FCFS":

        ans, gantt = fcfs(processes)

    # SJF

    elif algorithm == "SJF":

        ans, gantt = sjf(processes)

    # Priority

    elif algorithm == "Priority":

        ans, gantt = priority_scheduling(processes)

    # Round Robin

    elif algorithm == "Round Robin":

        ans, gantt = round_robin(processes, quantum)

    # EcoSched

    elif algorithm == "EcoSched":

        ans, gantt, total_energy = ecosched(processes)

        if total_energy is None:

            return jsonify({
                "error": "Energy calculation failed"
            }), 400

        run_id = save_simulation(
            algorithm,
            power_mode,
            quantum,
            total_energy,
            processes,
            ans
        )

        return jsonify({
            "algorithm": algorithm,
            "process_details": ans,
            "gantt_chart": gantt,
            "total_energy": total_energy,
            "run_id": run_id
        })

    # Calculate Energy for Traditional Algorithms

    total_energy = 0

    for process in processes:

        energy = calculate_energy(
            process["burst_time"],
            power_mode
        )

        if energy is None:

            return jsonify({
                "error": "Energy calculation failed"
            }), 400

        total_energy += energy[1]

    # Save Results

    run_id = save_simulation(
        algorithm,
        power_mode,
        quantum,
        total_energy,
        processes,
        ans
    )

    return jsonify({
        "algorithm": algorithm,
        "process_details": ans,
        "gantt_chart": gantt,
        "total_energy": total_energy,
        "run_id": run_id
    })


# Compare All Algorithms

@app.route("/compare", methods=["POST"])
def compare_algorithms():

    data, error = get_request_data()

    if error:

        return jsonify({"error": error}), 400

    processes, error = validate_processes(
        data.get("processes")
    )

    if error:

        return jsonify({"error": error}), 400

    quantum = data.get("quantum")

    if not validate_quantum(quantum):

        return jsonify({
            "error": "Time quantum must be positive"
        }), 400

    quantum = float(quantum)

    power_mode = data.get("power_mode")

    if not validate_power_mode(power_mode):

        return jsonify({
            "error": "Invalid power mode"
        }), 400

    results = []

    # Traditional Algorithm Energy

    total_energy = 0

    for process in processes:

        energy = calculate_energy(
            process["burst_time"],
            power_mode
        )

        if energy is None:

            return jsonify({
                "error": "Energy calculation failed"
            }), 400

        total_energy += energy[1]

    # FCFS

    ans, gantt = fcfs(processes)

    total_wt = sum(row[5] for row in ans)
    total_tat = sum(row[4] for row in ans)

    results.append([
        "FCFS",
        total_wt / len(ans),
        total_tat / len(ans),
        total_energy
    ])

    # SJF

    ans, gantt = sjf(processes)

    total_wt = sum(row[5] for row in ans)
    total_tat = sum(row[4] for row in ans)

    results.append([
        "SJF",
        total_wt / len(ans),
        total_tat / len(ans),
        total_energy
    ])

    # Priority

    ans, gantt = priority_scheduling(processes)

    total_wt = sum(row[5] for row in ans)
    total_tat = sum(row[4] for row in ans)

    results.append([
        "Priority",
        total_wt / len(ans),
        total_tat / len(ans),
        total_energy
    ])

    # Round Robin

    ans, gantt = round_robin(processes, quantum)

    total_wt = sum(row[5] for row in ans)
    total_tat = sum(row[4] for row in ans)

    results.append([
        "Round Robin",
        total_wt / len(ans),
        total_tat / len(ans),
        total_energy
    ])

    # EcoSched

    ans, gantt, eco_energy = ecosched(processes)

    total_wt = sum(row[7] for row in ans)
    total_tat = sum(row[6] for row in ans)

    results.append([
        "EcoSched",
        total_wt / len(ans),
        total_tat / len(ans),
        eco_energy
    ])

    return jsonify({
        "comparison": results
    })


# Get Simulation History

@app.route("/history", methods=["GET"])
def simulation_history():

    history = get_history()

    return jsonify({
        "history": history
    })


# Get Details of a Particular Simulation

@app.route("/history/<int:run_id>", methods=["GET"])
def simulation_details(run_id):

    details = get_simulation_details(run_id)

    return jsonify({
        "run_id": run_id,
        "details": details
    })


# Real-Time System Monitoring

@app.route("/system_metrics", methods=["GET"])
def system_metrics():

    try:

        metrics = get_system_metrics()

        return jsonify(metrics)

    except Exception:

        return jsonify({
            "error": "Unable to retrieve system metrics"
        }), 500


if __name__ == "__main__":

    app.run(debug=True)
