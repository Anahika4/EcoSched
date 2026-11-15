def fcfs(processes):
    p = processes.copy()
    # Sorting according to arrival time
    for i in range(len(p)):
        for j in range(i + 1, len(p)):
            if p[i]["arrival_time"] > p[j]["arrival_time"]:
                p[i], p[j] = p[j], p[i]
    t = 0
    ans = []
    gantt = []
    for i in range(len(p)):
        pid = p[i]["pid"]
        at = p[i]["arrival_time"]
        bt = p[i]["burst_time"]
        if t < at:
            gantt.append(["Idle", t, at])
            t = at
        ct = t + bt
        tat = ct - at
        wt = tat - bt
        ans.append([pid, at, bt, ct, tat, wt])
        gantt.append([pid, t, ct])
        t = ct
    return ans, gantt
def sjf(processes):
    p = processes.copy()

    t = 0
    count = 0
    n = len(p)

    done = [False] * n
    ans = []
    gantt = []

    while count < n:
        idx = -1
        mn = 999999

        # Find process with shortest burst time
        for i in range(n):
            if done[i] == False and p[i]["arrival_time"] <= t:
                if p[i]["burst_time"] < mn:
                    mn = p[i]["burst_time"]
                    idx = i

        # If no process has arrived
        if idx == -1:
            mn_at = 999999

            for i in range(n):
                if done[i] == False:
                    if p[i]["arrival_time"] < mn_at:
                        mn_at = p[i]["arrival_time"]

            gantt.append(["Idle", t, mn_at])
            t = mn_at

        else:
            pid = p[idx]["pid"]
            at = p[idx]["arrival_time"]
            bt = p[idx]["burst_time"]

            ct = t + bt
            tat = ct - at
            wt = tat - bt

            ans.append([pid, at, bt, ct, tat, wt])
            gantt.append([pid, t, ct])

            t = ct
            done[idx] = True
            count += 1

    return ans, gantt
def priority_scheduling(processes):
    p = processes.copy()

    t = 0
    count = 0
    n = len(p)

    done = [False] * n
    ans = []
    gantt = []

    while count < n:
        idx = -1
        mn = 999999

        # Find process with highest priority
        for i in range(n):
            if done[i] == False and p[i]["arrival_time"] <= t:
                if p[i]["priority"] < mn:
                    mn = p[i]["priority"]
                    idx = i

        # If no process has arrived
        if idx == -1:
            mn_at = 999999

            for i in range(n):
                if done[i] == False:
                    if p[i]["arrival_time"] < mn_at:
                        mn_at = p[i]["arrival_time"]

            gantt.append(["Idle", t, mn_at])
            t = mn_at

        else:
            pid = p[idx]["pid"]
            at = p[idx]["arrival_time"]
            bt = p[idx]["burst_time"]

            ct = t + bt
            tat = ct - at
            wt = tat - bt

            ans.append([pid, at, bt, ct, tat, wt])
            gantt.append([pid, t, ct])

            t = ct
            done[idx] = True
            count += 1

    return ans, gantt
def round_robin(processes, tq):
    p = processes.copy()

    n = len(p)
    rem = []

    for i in range(n):
        rem.append(p[i]["burst_time"])

    t = 0
    count = 0
    queue = []
    added = [False] * n

    ans = []
    gantt = []

    while count < n:

        # Add processes that have arrived
        for i in range(n):
            if added[i] == False and p[i]["arrival_time"] <= t:
                queue.append(i)
                added[i] = True

        # If ready queue is empty
        if len(queue) == 0:
            mn_at = 999999

            for i in range(n):
                if added[i] == False:
                    if p[i]["arrival_time"] < mn_at:
                        mn_at = p[i]["arrival_time"]

            gantt.append(["Idle", t, mn_at])
            t = mn_at
            continue

        # Select first process from queue
        idx = queue.pop(0)

        pid = p[idx]["pid"]
        at = p[idx]["arrival_time"]

        if rem[idx] > tq:
            st = t
            t = t + tq
            rem[idx] = rem[idx] - tq

        else:
            st = t
            t = t + rem[idx]
            rem[idx] = 0

        gantt.append([pid, st, t])

        # Add newly arrived processes
        for i in range(n):
            if added[i] == False and p[i]["arrival_time"] <= t:
                queue.append(i)
                added[i] = True

        # If process is not completed, add it again
        if rem[idx] > 0:
            queue.append(idx)

        else:
            ct = t
            tat = ct - at
            wt = tat - p[idx]["burst_time"]

            ans.append([pid, at, p[idx]["burst_time"], ct, tat, wt])
            count += 1

    return ans, gantt

def ecosched(processes):
    from energy_calculator import calculate_energy

    p = processes.copy()

    n = len(p)
    done = [False] * n

    t = 0
    count = 0

    ans = []
    gantt = []
    total_energy = 0

    while count < n:
        idx = -1
        mn = 999999

        # Select shortest available process
        for i in range(n):
            if done[i] == False and p[i]["arrival_time"] <= t:
                if p[i]["burst_time"] < mn:
                    mn = p[i]["burst_time"]
                    idx = i

        # If no process has arrived
        if idx == -1:
            mn_at = 999999

            for i in range(n):
                if done[i] == False:
                    if p[i]["arrival_time"] < mn_at:
                        mn_at = p[i]["arrival_time"]

            gantt.append(["Idle", t, mn_at])
            t = mn_at

        else:
            pid = p[idx]["pid"]
            at = p[idx]["arrival_time"]
            bt = p[idx]["burst_time"]
            priority = p[idx]["priority"]

            # Select power mode
            if priority == 1:
                mode = "High"
            elif priority == 2:
                mode = "Medium"
            else:
                mode = "Low"

            # Calculate execution time and energy
            energy = calculate_energy(bt, mode)

            if energy == None:
                return None

            et = energy[0]
            energy_used = energy[1]

            ct = t + et
            tat = ct - at
            wt = tat - et

            ans.append([
                pid, at, bt, mode, et, ct, tat, wt, energy_used
            ])

            gantt.append([pid, t, ct, mode])

            total_energy = total_energy + energy_used

            t = ct
            done[idx] = True
            count += 1

    return ans, gantt, total_energy
