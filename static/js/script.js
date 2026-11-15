
var processCount = 3;

var waitingChart = null;
var turnaroundChart = null;
var energyChart = null;


// ADD PROCESS

function addProcess() {
    processCount++;

    var tbody = document.querySelector("#processTable tbody");
    var row = tbody.insertRow();

    row.innerHTML = `
        <td>P${processCount}</td>
        <td><input type="number" class="form-control" value="0" min="0"></td>
        <td><input type="number" class="form-control" value="1" min="1"></td>
        <td><input type="number" class="form-control" value="1" min="1"></td>
    `;
}


// REMOVE PROCESS

function removeProcess() {
    var tbody = document.querySelector("#processTable tbody");

    if (tbody.rows.length > 1) {
        tbody.deleteRow(tbody.rows.length - 1);
        processCount--;
    }
}


// GET PROCESS DETAILS

function getProcesses() {
    var rows = document.querySelector("#processTable tbody").rows;
    var processes = [];

    for (var i = 0; i < rows.length; i++) {
        var inputs = rows[i].getElementsByTagName("input");

        var arrival = Number(inputs[0].value);
        var burst = Number(inputs[1].value);
        var priority = Number(inputs[2].value);

        if (
            inputs[0].value === "" ||
            inputs[1].value === "" ||
            inputs[2].value === "" ||
            !Number.isFinite(arrival) ||
            !Number.isFinite(burst) ||
            !Number.isFinite(priority) ||
            arrival < 0 ||
            burst <= 0 ||
            priority <= 0 ||
            !Number.isInteger(priority)
        ) {
            document.getElementById("errorMessage").innerText =
                "Please enter valid process details.";

            return null;
        }

        processes.push({
            pid: rows[i].cells[0].innerText,
            arrival_time: arrival,
            burst_time: burst,
            priority: priority
        });
    }

    return processes;
}


// VALIDATE TIME QUANTUM

function getQuantum() {
    var quantum = Number(document.getElementById("quantum").value);

    if (
        document.getElementById("quantum").value === "" ||
        !Number.isFinite(quantum) ||
        quantum <= 0 ||
        !Number.isInteger(quantum)
    ) {
        document.getElementById("errorMessage").innerText =
            "Time quantum must be a positive integer.";

        return null;
    }

    return quantum;
}


// RUN SELECTED ALGORITHM

function runSimulation() {
    var processes = getProcesses();

    if (processes === null) {
        return;
    }

    var quantum = getQuantum();

    if (quantum === null) {
        return;
    }

    var algorithm = document.getElementById("algorithm").value;
    var powerMode = document.getElementById("powerMode").value;

    document.getElementById("errorMessage").innerText = "";

    fetch("/run", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            processes: processes,
            algorithm: algorithm,
            quantum: quantum,
            power_mode: powerMode
        })
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.error) {
            document.getElementById("errorMessage").innerText = data.error;
            return;
        }

        displayResults(data);
        loadHistory();
    })
    .catch(function(error) {
        document.getElementById("errorMessage").innerText =
            "Something went wrong. Please try again.";

        console.log(error);
    });
}


// DISPLAY SCHEDULING RESULTS

function displayResults(data) {
    document.getElementById("results").style.display = "block";

    document.getElementById("selectedAlgorithm").innerText =
        "Selected Algorithm: " + data.algorithm;

    var table = document.getElementById("resultTable");
    table.innerHTML = "";

    var headers;

    if (data.algorithm === "EcoSched") {
        headers = [
            "PID", "Arrival Time", "Burst Time", "Power Mode",
            "Execution Time", "Completion Time", "Turnaround Time",
            "Waiting Time", "Energy (J)"
        ];
    } else {
        headers = [
            "PID", "Arrival Time", "Burst Time",
            "Completion Time", "Turnaround Time", "Waiting Time"
        ];
    }

    var headerRow = table.insertRow();

    headers.forEach(function(header) {
        var cell = document.createElement("th");
        cell.innerText = header;
        headerRow.appendChild(cell);
    });

    data.process_details.forEach(function(process) {
        var row = table.insertRow();

        process.forEach(function(value) {
            var cell = row.insertCell();
            cell.innerText = value;
        });
    });

    document.getElementById("totalEnergy").innerText =
        Number(data.total_energy).toFixed(2) + " Joules";

    displayGanttChart(data.gantt_chart);

    document.getElementById("results").scrollIntoView({
        behavior: "smooth"
    });
}


// DISPLAY GANTT CHART

function displayGanttChart(ganttData) {
    var gantt = document.getElementById("ganttChart");
    gantt.innerHTML = "";

    ganttData.forEach(function(process) {
        var box = document.createElement("div");
        box.className = "gantt-box";

        var heading = document.createElement("strong");
        heading.innerText = process[0];

        if (process.length === 4) {
            heading.innerText += " (" + process[3] + ")";
        }

        var time = document.createElement("div");
        time.innerText = process[1] + " - " + process[2];

        box.appendChild(heading);
        box.appendChild(time);
        gantt.appendChild(box);
    });
}


// COMPARE ALL ALGORITHMS

function compareAlgorithms() {
    var processes = getProcesses();

    if (processes === null) {
        return;
    }

    var quantum = getQuantum();

    if (quantum === null) {
        return;
    }

    var powerMode = document.getElementById("powerMode").value;

    document.getElementById("errorMessage").innerText = "";

    fetch("/compare", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            processes: processes,
            quantum: quantum,
            power_mode: powerMode
        })
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.error) {
            document.getElementById("errorMessage").innerText = data.error;
            return;
        }

        displayComparisonTable(data.comparison);
        displayComparisonCharts(data.comparison);

        document.getElementById("comparisonResults").style.display = "block";

        document.getElementById("comparisonResults").scrollIntoView({
            behavior: "smooth"
        });
    })
    .catch(function(error) {
        document.getElementById("errorMessage").innerText =
            "Unable to compare algorithms.";

        console.log(error);
    });
}


// DISPLAY COMPARISON TABLE

function displayComparisonTable(comparison) {
    var table = document.getElementById("comparisonTable");
    table.innerHTML = "";

    var headers = [
        "Algorithm",
        "Average Waiting Time",
        "Average Turnaround Time",
        "Total Energy (J)"
    ];

    var headerRow = table.insertRow();

    headers.forEach(function(header) {
        var cell = document.createElement("th");
        cell.innerText = header;
        headerRow.appendChild(cell);
    });

    comparison.forEach(function(result) {
        var row = table.insertRow();

        result.forEach(function(value, index) {
            var cell = row.insertCell();

            cell.innerText = index === 0
                ? value
                : Number(value).toFixed(2);
        });

        if (result[0] === "EcoSched") {
            row.style.backgroundColor = "#dcfce7";
            row.style.fontWeight = "bold";
        }
    });
}


// DISPLAY COMPARISON CHARTS

function displayComparisonCharts(comparison) {
    var labels = comparison.map(function(row) {
        return row[0];
    });

    var waitingTimes = comparison.map(function(row) {
        return row[1];
    });

    var turnaroundTimes = comparison.map(function(row) {
        return row[2];
    });

    var energyValues = comparison.map(function(row) {
        return row[3];
    });

    if (waitingChart) waitingChart.destroy();
    if (turnaroundChart) turnaroundChart.destroy();
    if (energyChart) energyChart.destroy();

    waitingChart = createChart(
        "waitingChart",
        "Average Waiting Time",
        labels,
        waitingTimes,
        "#3b82f6"
    );

    turnaroundChart = createChart(
        "turnaroundChart",
        "Average Turnaround Time",
        labels,
        turnaroundTimes,
        "#16a34a"
    );

    energyChart = createChart(
        "energyChart",
        "Energy Consumption (Joules)",
        labels,
        energyValues,
        "#f59e0b"
    );
}


// CREATE BAR CHART

function createChart(id, title, labels, values, color) {
    return new Chart(document.getElementById(id), {
        type: "bar",

        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: values,
                backgroundColor: color
            }]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}


// LOAD SIMULATION HISTORY

function loadHistory() {
    var table = document.getElementById("historyTable");

    table.innerHTML =
        "<tr><td colspan='7'>Loading history...</td></tr>";

    fetch("/history")
    .then(function(response) {
        if (!response.ok) {
            throw new Error("History request failed");
        }

        return response.json();
    })
    .then(function(data) {
        table.innerHTML = "";

        if (!data.history || data.history.length === 0) {
            table.innerHTML =
                "<tr><td colspan='7'>No simulation history found.</td></tr>";
            return;
        }

        data.history.forEach(function(run) {
            var row = table.insertRow();

            var values = [
                run.id,
                run.algorithm,
                run.power_mode,
                run.quantum,
                Number(run.total_energy).toFixed(2),
                run.created_at
            ];

            values.forEach(function(value) {
                var cell = row.insertCell();
                cell.innerText = value;
            });

            var buttonCell = row.insertCell();
            var button = document.createElement("button");

            button.className = "btn btn-sm btn-outline-primary";
            button.innerText = "View Details";

            button.onclick = function() {
                showHistoryDetails(run.id);
            };

            buttonCell.appendChild(button);
        });
    })
    .catch(function(error) {
        table.innerHTML =
            "<tr><td colspan='7'>Unable to load history.</td></tr>";

        console.log(error);
    });
}


// SHOW PREVIOUS SIMULATION DETAILS

function showHistoryDetails(runId) {
    fetch("/history/" + runId)
    .then(function(response) {
        if (!response.ok) {
            throw new Error("Details request failed");
        }

        return response.json();
    })
    .then(function(data) {
        var details = data.details;
        var table = document.getElementById("historyDetailsTable");

        table.innerHTML = "";

        document.getElementById("historyRunTitle").innerText =
            "Simulation Run ID: " + runId;

        var headers = [
            "PID", "Arrival Time", "Burst Time", "Priority",
            "Power Mode", "Execution Time", "Completion Time",
            "Turnaround Time", "Waiting Time", "Energy (J)"
        ];

        var headerRow = table.insertRow();

        headers.forEach(function(header) {
            var cell = document.createElement("th");
            cell.innerText = header;
            headerRow.appendChild(cell);
        });

        details.forEach(function(process) {
            var values = [
                process.pid,
                process.arrival_time,
                process.burst_time,
                process.priority,
                process.selected_power_mode,
                process.execution_time,
                process.completion_time,
                process.turnaround_time,
                process.waiting_time,
                process.energy_used
            ];

            var row = table.insertRow();

            values.forEach(function(value) {
                var cell = row.insertCell();
                cell.innerText = value;
            });
        });

        document.getElementById("historyDetails").style.display = "block";

        document.getElementById("historyDetails").scrollIntoView({
            behavior: "smooth"
        });
    })
    .catch(function(error) {
        document.getElementById("errorMessage").innerText =
            "Unable to load simulation details.";

        console.log(error);
    });
}


// LOAD REAL-TIME SYSTEM METRICS

function loadSystemMetrics() {
    var message = document.getElementById("systemMetricsMessage");

    message.innerText = "Updating system metrics...";

    fetch("/system_metrics")
    .then(function(response) {
        if (!response.ok) {
            throw new Error("Unable to fetch system metrics");
        }

        return response.json();
    })
    .then(function(data) {
        document.getElementById("cpuUsage").innerText =
            data.cpu_usage + "%";

        document.getElementById("memoryUsage").innerText =
            data.memory_usage + "%";

        document.getElementById("memoryDetails").innerText =
            "Used: " + data.used_memory + " GB / " +
            "Total: " + data.total_memory + " GB";

        document.getElementById("batteryPercentage").innerText =
            data.battery_percentage === null
                ? "Not Available"
                : data.battery_percentage + "%";

        document.getElementById("chargingStatus").innerText =
            data.charging_status;

        message.innerText = "Metrics updated successfully.";
    })
    .catch(function(error) {
        message.innerText =
            "Unable to load system metrics. Check the Flask server.";

        console.log(error);
    });
}
// LOAD DATA WHEN DASHBOARD OPENS
window.onload = function() {
    loadHistory();
    loadSystemMetrics();
};
