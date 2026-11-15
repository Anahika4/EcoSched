
import unittest
import copy

from scheduler import (
    fcfs,
    sjf,
    priority_scheduling,
    round_robin,
    ecosched
)

from energy_calculator import calculate_energy


# Main Test Dataset

TEST_PROCESSES = [
    {
        "pid": "P1",
        "arrival_time": 0,
        "burst_time": 5,
        "priority": 2
    },
    {
        "pid": "P2",
        "arrival_time": 1,
        "burst_time": 3,
        "priority": 1
    },
    {
        "pid": "P3",
        "arrival_time": 2,
        "burst_time": 8,
        "priority": 3
    },
    {
        "pid": "P4",
        "arrival_time": 3,
        "burst_time": 2,
        "priority": 2
    },
    {
        "pid": "P5",
        "arrival_time": 4,
        "burst_time": 4,
        "priority": 1
    }
]


# Dataset with CPU Idle Time

IDLE_PROCESSES = [
    {
        "pid": "P1",
        "arrival_time": 2,
        "burst_time": 3,
        "priority": 2
    },
    {
        "pid": "P2",
        "arrival_time": 8,
        "burst_time": 2,
        "priority": 1
    },
    {
        "pid": "P3",
        "arrival_time": 4,
        "burst_time": 1,
        "priority": 3
    }
]


class EcoSchedTests(unittest.TestCase):

    # Check Gantt Chart

    def check_gantt(self, gantt, processes):

        self.assertIsInstance(gantt, list)
        self.assertGreater(len(gantt), 0)

        expected_pids = {
            process["pid"] for process in processes
        }

        actual_pids = set()
        previous_end = None

        for item in gantt:

            self.assertGreaterEqual(len(item), 3)

            pid = item[0]
            start = float(item[1])
            end = float(item[2])

            self.assertGreater(end, start)

            if previous_end is not None:
                self.assertGreaterEqual(
                    start,
                    previous_end - 0.000001
                )

            previous_end = end

            if pid != "Idle":
                actual_pids.add(pid)

        self.assertEqual(actual_pids, expected_pids)

    # Check Traditional Scheduling Algorithms

    def check_standard_algorithm(self, algorithm, processes):

        data = copy.deepcopy(processes)

        ans, gantt = algorithm(data)

        self.assertEqual(len(ans), len(processes))

        result_pids = set()

        for row in ans:

            self.assertEqual(len(row), 6)

            pid = row[0]
            arrival = float(row[1])
            burst = float(row[2])
            completion = float(row[3])
            turnaround = float(row[4])
            waiting = float(row[5])

            result_pids.add(pid)

            self.assertAlmostEqual(
                turnaround,
                completion - arrival
            )

            self.assertAlmostEqual(
                waiting,
                turnaround - burst
            )

            self.assertGreaterEqual(waiting, -0.000001)

        expected_pids = {
            process["pid"] for process in processes
        }

        self.assertEqual(result_pids, expected_pids)

        self.check_gantt(gantt, processes)

    # FCFS Test

    def test_fcfs(self):

        self.check_standard_algorithm(
            fcfs,
            TEST_PROCESSES
        )

    # SJF Test

    def test_sjf(self):

        self.check_standard_algorithm(
            sjf,
            TEST_PROCESSES
        )

    # Priority Test

    def test_priority(self):

        self.check_standard_algorithm(
            priority_scheduling,
            TEST_PROCESSES
        )

    # Round Robin Test

    def test_round_robin(self):

        data = copy.deepcopy(TEST_PROCESSES)

        ans, gantt = round_robin(data, 2)

        self.assertEqual(len(ans), len(TEST_PROCESSES))

        result_pids = set()

        for row in ans:

            self.assertEqual(len(row), 6)

            pid = row[0]
            arrival = float(row[1])
            burst = float(row[2])
            completion = float(row[3])
            turnaround = float(row[4])
            waiting = float(row[5])

            result_pids.add(pid)

            self.assertAlmostEqual(
                turnaround,
                completion - arrival
            )

            self.assertAlmostEqual(
                waiting,
                turnaround - burst
            )

            self.assertGreaterEqual(waiting, -0.000001)

        expected_pids = {
            process["pid"] for process in TEST_PROCESSES
        }

        self.assertEqual(result_pids, expected_pids)

        self.check_gantt(gantt, TEST_PROCESSES)

    # EcoSched Test

    def test_ecosched(self):

        data = copy.deepcopy(TEST_PROCESSES)

        ans, gantt, total_energy = ecosched(data)

        self.assertEqual(len(ans), len(TEST_PROCESSES))

        self.assertIsNotNone(total_energy)
        self.assertGreaterEqual(total_energy, 0)

        result_pids = set()
        calculated_energy = 0

        for row in ans:

            self.assertEqual(len(row), 9)

            pid = row[0]
            arrival = float(row[1])
            burst = float(row[2])
            mode = row[3]
            execution = float(row[4])
            completion = float(row[5])
            turnaround = float(row[6])
            waiting = float(row[7])
            energy = float(row[8])

            result_pids.add(pid)

            self.assertIn(
                mode,
                ["Low", "Medium", "High"]
            )

            self.assertGreater(execution, 0)
            self.assertGreater(energy, 0)

            self.assertAlmostEqual(
                turnaround,
                completion - arrival
            )

            # EcoSched uses simulated execution time

            self.assertAlmostEqual(
                waiting,
                turnaround - execution
            )

            self.assertGreaterEqual(waiting, -0.000001)

            calculated_energy += energy

        expected_pids = {
            process["pid"] for process in TEST_PROCESSES
        }

        self.assertEqual(result_pids, expected_pids)

        self.assertAlmostEqual(
            calculated_energy,
            total_energy
        )

        self.check_gantt(gantt, TEST_PROCESSES)

    # CPU Idle Time Test

    def test_cpu_idle_time(self):

        algorithms = [
            fcfs,
            sjf,
            priority_scheduling
        ]

        for algorithm in algorithms:

            with self.subTest(algorithm=algorithm.__name__):

                self.check_standard_algorithm(
                    algorithm,
                    IDLE_PROCESSES
                )

    # Round Robin Idle Time Test

    def test_round_robin_idle_time(self):

        data = copy.deepcopy(IDLE_PROCESSES)

        ans, gantt = round_robin(data, 2)

        self.assertEqual(len(ans), len(IDLE_PROCESSES))

        self.check_gantt(gantt, IDLE_PROCESSES)

        for row in ans:

            self.assertAlmostEqual(
                float(row[4]),
                float(row[3]) - float(row[1])
            )

            self.assertAlmostEqual(
                float(row[5]),
                float(row[4]) - float(row[2])
            )

    # Energy Calculator Test

    def test_energy_calculator(self):

        low = calculate_energy(4, "Low")
        medium = calculate_energy(4, "Medium")
        high = calculate_energy(4, "High")

        self.assertAlmostEqual(low[0], 8)
        self.assertAlmostEqual(low[1], 16)

        self.assertAlmostEqual(medium[0], 4)
        self.assertAlmostEqual(medium[1], 20)

        self.assertAlmostEqual(high[0], 2)
        self.assertAlmostEqual(high[1], 24)

    # Invalid Power Mode Test

    def test_invalid_power_mode(self):

        result = calculate_energy(4, "Invalid")

        self.assertIsNone(result)


if __name__ == "__main__":

    print("\n========== ECOSCHED TESTING ==========\n")

    unittest.main(verbosity=2)
