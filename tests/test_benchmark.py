import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from arena.benchmark import benchmark


class BenchmarkTests(unittest.TestCase):
    def test_timer_and_repeat_contract(self):
        a = [3, 1, 2]
        with patch("arena.benchmark.time.perf_counter_ns", side_effect=range(0, 120, 10)):
            result = benchmark(a, repeats=2)
        self.assertEqual(a, [3, 1, 2])
        for row in result["results"]:
            self.assertEqual(row["samples_ns"], [10, 10])
            self.assertEqual(row["median_ns"], 10)
            self.assertEqual(row["recorded_events"], 0)
        for invalid in [0, -1, True, 1.5]:
            with self.assertRaises(ValueError):
                benchmark(a, invalid)

    def test_cli_exports_and_errors(self):
        with tempfile.TemporaryDirectory() as folder:
            command = [
                sys.executable,
                "-m",
                "arena",
                "--values",
                "3,-1,3,0",
                "--repeats",
                "2",
                "--trace",
                "--output",
                folder,
            ]
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            report = json.loads((Path(folder) / "benchmark.json").read_text())
            self.assertEqual(len(report["results"]), 3)
            for name in ["merge", "quick", "heap"]:
                trace = json.loads((Path(folder) / f"{name}_trace.json").read_text())
                self.assertEqual(trace["output"], [-1, 0, 3, 3])
            self.assertTrue((Path(folder) / "comparison.csv").exists())
            bad = subprocess.run(
                [sys.executable, "-m", "arena", "--size", "-1"], capture_output=True
            )
            self.assertNotEqual(bad.returncode, 0)
