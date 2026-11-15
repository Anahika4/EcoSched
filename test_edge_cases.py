
import unittest
import copy

from scheduler import (
    fcfs,
    sjf,
    priority_scheduling,
    round_robin,
    ecosched
)


class EdgeCaseTests(unittest.TestCase):

    def setUp(self):

        # Single process

        self.single_process = [
            {
                "pid": "P1",
                "arrival_time": 0,
                "burst_time": 5,
                "priority": 1
            }
        ]

        # All processes arrive at the same time

        self.same_arrival = [
            {
                "pid": "P1",
                "arrival_time": 0,
                "burst_time": 5,
                "priority": 2
            },
            {
                "pid": "P2",
                "arrival_time": 0,
                "burst_time": 3,
                "priority": 1
            },
            {
                "pid": "P3",
                "arrival_time": 0,
                "burst_time": 2,
                "priority": 3
            }
        ]

        # Different arrival times

        self.different_arrival = [
            {
                "pid": "P1",
                "arrival_time": 0,
                "burst_time": 2,
                "priority": 2
            },
            {
                "pid": "P2",
                "arrival_time": 5,
                "burst_time": 3,
                "priority": 1
            }
        ]

    # Check traditional algorithm output

    def check_standard(self, algorithm, processes):

        data = copy.deepcopy(processes)

        ans, gantt = algorithm(data)

        self.assertEqual(len(ans), len(processes))

        self.assertEqual(
            {row[0] for row in ans},
            {p["pid"] for p in processes}
        )

        for row in ans:

            arrival = float(row[1])
            burst = float(row[2])
            completion = float(row[3])
            turnaround = float(row[4])
            waiting = float(row[5])

            self.assertAlmostEqual(
                turnaround,
                completion - arrival
            )

            self.assertAlmostEqual(
                waiting,
                turnaround - burst
            )

            self.assertGreaterEqual(waiting, -0.000001)

        self.assertGreater(len(gantt), 0)

    # Check EcoSched output

    def check_ecosched(self, processes):

        data = copy.deepcopy(processes)

        ans, gantt, total_energy = ecosched(data)

        self.assertEqual(len(ans), len(processes))

        self.assertIsNotNone(total_energy)

        calculated_energy = 0

        for row in ans:

            arrival = float(row[1])
            burst = float(row[2])
            execution = float(row[4])
            completion = float(row[5])
            turnaround = float(row[6])
            waiting = float(row[7])
            energy = float(row[8])

            self.assertGreater(execution, 0)
            self.assertGreater(energy, 0)

            self.assertAlmostEqual(
                turnaround,
                completion - arrival
            )

            self.assertAlmostEqual(
                waiting,
                turnaround - execution
            )

            self.assertGreaterEqual(waiting, -0.000001)

            calculated_energy += energy

        self.assertAlmostEqual(
            calculated_energy,
            total_energy
        )

        self.assertGreater(len(gantt), 0)

    # Test 1: Single process in FCFS

    def test_single_process_fcfs(self):

        self.check_standard(
            fcfs,
            self.single_process
        )

    # Test 2: Single process in SJF

    def test_single_process_sjf(self):

        self.check_standard(
            sjf,
            self.single_process
        )

    # Test 3: Single process in Priority

    def test_single_process_priority(self):

        self.check_standard(
            priority_scheduling,
            self.single_process
        )

    # Test 4: Single process in Round Robin

    def test_single_process_round_robin(self):

        ans, gantt = round_robin(
            copy.deepcopy(self.single_process),
            2
        )

        self.assertEqual(len(ans), 1)
        self.assertEqual(ans[0][0], "P1")

    # Test 5: Single process in EcoSched

    def test_single_process_ecosched(self):

        self.check_ecosched(
            self.single_process
        )

    # Test 6: Same arrival time in FCFS

    def test_same_arrival_fcfs(self):

        self.check_standard(
            fcfs,
            self.same_arrival
        )

    # Test 7: Same arrival time in SJF

    def test_same_arrival_sjf(self):

        self.check_standard(
            sjf,
            self.same_arrival
        )

    # Test 8: Same arrival time in Priority

    def test_same_arrival_priority(self):

        self.check_standard(
            priority_scheduling,
            self.same_arrival
        )

    # Test 9: Same arrival time in Round Robin

    def test_same_arrival_round_robin(self):

        ans, gantt = round_robin(
            copy.deepcopy(self.same_arrival),
            2
        )

        self.assertEqual(len(ans), 3)

        self.assertEqual(
            {row[0] for row in ans},
            {"P1", "P2", "P3"}
        )

    # Test 10: Same arrival time in EcoSched

    def test_same_arrival_ecosched(self):

        self.check_ecosched(
            self.same_arrival
        )

    # Test 11: Large Round Robin quantum

    def test_large_quantum(self):

        ans, gantt = round_robin(
            copy.deepcopy(self.same_arrival),
            100
        )

        self.assertEqual(len(ans), 3)

        for row in ans:

            self.assertAlmostEqual(
                float(row[4]),
                float(row[3]) - float(row[1])
            )

            self.assertAlmostEqual(
                float(row[5]),
                float(row[4]) - float(row[2])
            )

    # Test 12: Processes arriving after CPU idle time

    def test_late_arrival(self):

        for algorithm in [
            fcfs,
            sjf,
            priority_scheduling
        ]:

            with self.subTest(algorithm=algorithm.__name__):

                self.check_standard(
                    algorithm,
                    self.different_arrival
                )

    # Test 13: EcoSched with late arrival

    def test_ecosched_late_arrival(self):

        self.check_ecosched(
            self.different_arrival
        )


if __name__ == "__main__":

    print("\n========== ECOSCHED EDGE CASE TESTING ==========\n")

    unittest.main(verbosity=2)
