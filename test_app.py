
import unittest
from unittest.mock import patch

from app import app


class EcoSchedAppTests(unittest.TestCase):

    def setUp(self):

        self.client = app.test_client()

        self.processes = [
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
                "burst_time": 4,
                "priority": 3
            }
        ]

        self.data = {
            "processes": self.processes,
            "algorithm": "FCFS",
            "quantum": 2,
            "power_mode": "Medium"
        }

    # Dashboard

    def test_home_page(self):

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)

    # FCFS

    @patch("app.save_simulation", return_value=999)
    def test_run_fcfs(self, mock_save):

        response = self.client.post(
            "/run",
            json=self.data
        )

        self.assertEqual(response.status_code, 200)

        result = response.get_json()

        self.assertEqual(result["algorithm"], "FCFS")
        self.assertEqual(len(result["process_details"]), 3)

    # SJF

    @patch("app.save_simulation", return_value=999)
    def test_run_sjf(self, mock_save):

        data = self.data.copy()
        data["algorithm"] = "SJF"

        response = self.client.post("/run", json=data)

        self.assertEqual(response.status_code, 200)

    # Priority

    @patch("app.save_simulation", return_value=999)
    def test_run_priority(self, mock_save):

        data = self.data.copy()
        data["algorithm"] = "Priority"

        response = self.client.post("/run", json=data)

        self.assertEqual(response.status_code, 200)

    # Round Robin

    @patch("app.save_simulation", return_value=999)
    def test_run_round_robin(self, mock_save):

        data = self.data.copy()
        data["algorithm"] = "Round Robin"

        response = self.client.post("/run", json=data)

        self.assertEqual(response.status_code, 200)

    # EcoSched

    @patch("app.save_simulation", return_value=999)
    def test_run_ecosched(self, mock_save):

        data = self.data.copy()
        data["algorithm"] = "EcoSched"

        response = self.client.post("/run", json=data)

        self.assertEqual(response.status_code, 200)

        result = response.get_json()

        self.assertEqual(result["algorithm"], "EcoSched")
        self.assertIn("total_energy", result)

    # Empty processes

    def test_empty_processes(self):

        data = self.data.copy()
        data["processes"] = []

        response = self.client.post("/run", json=data)

        self.assertEqual(response.status_code, 400)

    # Invalid algorithm

    def test_invalid_algorithm(self):

        data = self.data.copy()
        data["algorithm"] = "Invalid"

        response = self.client.post("/run", json=data)

        self.assertEqual(response.status_code, 400)

    # Invalid quantum

    def test_invalid_quantum(self):

        data = self.data.copy()
        data["algorithm"] = "Round Robin"
        data["quantum"] = 0

        response = self.client.post("/run", json=data)

        self.assertEqual(response.status_code, 400)

    # Comparison

    def test_comparison(self):

        response = self.client.post(
            "/compare",
            json={
                "processes": self.processes,
                "quantum": 2,
                "power_mode": "Medium"
            }
        )

        self.assertEqual(response.status_code, 200)

        result = response.get_json()

        self.assertEqual(len(result["comparison"]), 5)

    # History

    def test_history(self):

        response = self.client.get("/history")

        self.assertEqual(response.status_code, 200)

        self.assertIn("history", response.get_json())

    # System monitoring

    def test_system_metrics(self):

        response = self.client.get("/system_metrics")

        self.assertEqual(response.status_code, 200)

        metrics = response.get_json()

        required_keys = [
            "cpu_usage",
            "memory_usage",
            "total_memory",
            "used_memory",
            "available_memory",
            "battery_percentage",
            "charging_status"
        ]

        for key in required_keys:

            self.assertIn(key, metrics)

    # Simulation details

    def test_simulation_details(self):

        response = self.client.get("/history/999999")

        self.assertEqual(response.status_code, 200)

        result = response.get_json()

        self.assertIn("run_id", result)
        self.assertIn("details", result)

    # Invalid arrival time

    def test_negative_arrival_time(self):

        data = self.data.copy()
        data["processes"] = [p.copy() for p in self.processes]

        data["processes"][0]["arrival_time"] = -5

        response = self.client.post("/run", json=data)

        self.assertEqual(response.status_code, 400)

    # Zero burst time

    def test_zero_burst_time(self):

        data = self.data.copy()
        data["processes"] = [p.copy() for p in self.processes]

        data["processes"][0]["burst_time"] = 0

        response = self.client.post("/run", json=data)

        self.assertEqual(response.status_code, 400)

    # Negative burst time

    def test_negative_burst_time(self):

        data = self.data.copy()
        data["processes"] = [p.copy() for p in self.processes]

        data["processes"][0]["burst_time"] = -3

        response = self.client.post("/run", json=data)

        self.assertEqual(response.status_code, 400)

    # Missing priority

    def test_missing_priority(self):

        data = self.data.copy()
        data["processes"] = [p.copy() for p in self.processes]

        del data["processes"][0]["priority"]

        response = self.client.post("/run", json=data)

        self.assertEqual(response.status_code, 400)

    # Missing burst time

    def test_missing_burst_time(self):

        data = self.data.copy()
        data["processes"] = [p.copy() for p in self.processes]

        del data["processes"][0]["burst_time"]

        response = self.client.post("/run", json=data)

        self.assertEqual(response.status_code, 400)

    # Duplicate process ID

    def test_duplicate_pid(self):

        data = self.data.copy()
        data["processes"] = [p.copy() for p in self.processes]

        data["processes"][1]["pid"] = "P1"

        response = self.client.post("/run", json=data)

        self.assertEqual(response.status_code, 400)

    # Invalid priority

    def test_invalid_priority(self):

        data = self.data.copy()
        data["processes"] = [p.copy() for p in self.processes]

        data["processes"][0]["priority"] = 0

        response = self.client.post("/run", json=data)

        self.assertEqual(response.status_code, 400)

    # Non-numeric burst time

    def test_non_numeric_burst(self):

        data = self.data.copy()
        data["processes"] = [p.copy() for p in self.processes]

        data["processes"][0]["burst_time"] = "abc"

        response = self.client.post("/run", json=data)

        self.assertEqual(response.status_code, 400)

    # Invalid power mode

    def test_invalid_power_mode(self):

        data = self.data.copy()
        data["power_mode"] = "Super"

        response = self.client.post("/run", json=data)

        self.assertEqual(response.status_code, 400)

    # Invalid comparison input

    def test_invalid_comparison_input(self):

        data = {
            "processes": self.processes,
            "quantum": -1,
            "power_mode": "Medium"
        }

        response = self.client.post("/compare", json=data)

        self.assertEqual(response.status_code, 400)

    # Missing JSON

    def test_missing_json(self):

        response = self.client.post(
            "/run",
            data="",
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":

    print("\n========== ECOSCHED FLASK API TESTING ==========\n")

    unittest.main(verbosity=2)
