import itertools
import random
import unittest
from arena.sorting import ALGORITHMS, run_sort


class SortingTests(unittest.TestCase):
    def test_exhaustive_and_seeded(self):
        cases = [list(x) for n in range(6) for x in itertools.product([-1, 0, 1], repeat=n)]
        rng = random.Random(42)
        cases += [[rng.randint(-100, 100) for _ in range(n)] for n in range(60)]
        for name, function in ALGORITHMS.items():
            for a in cases:
                original = a[:]
                result = run_sort(a, name, trace=False)
                plain = a[:]
                function(plain)
                self.assertEqual(result["output"], sorted(a), (name, a))
                self.assertEqual(plain, sorted(a), (name, a))
                self.assertEqual(a, original)

    def test_replay_and_metrics(self):
        for name in ALGORITHMS:
            result = run_sort([5, -2, 5, 0, 1], name)
            state = result["input"][:]
            counts = dict(comparisons=0, swaps=0, writes=0)
            for event in result["events"]:
                kind = event["kind"]
                if kind == "compare":
                    counts["comparisons"] += 1
                    x, y = event["values"]
                    op = event["operator"]
                    expected = x <= y if op == "<=" else (x < y if op == "<" else x > y)
                    self.assertEqual(event["result"], expected)
                elif kind == "swap":
                    i, j = event["indices"]
                    state[i], state[j] = state[j], state[i]
                    self.assertEqual([state[i], state[j]], event["values"])
                    counts["swaps"] += 1
                    counts["writes"] += 2
                elif kind == "write":
                    state[event["index"]] = event["value"]
                    counts["writes"] += 1
            self.assertEqual(state, result["output"])
            self.assertEqual(result["events"][0]["array"], [5, -2, 5, 0, 1])
            self.assertEqual(result["events"][-1]["array"], state)
            for k, v in counts.items():
                self.assertEqual(result["metrics"][k], v)
            limited = run_sort(result["input"], name, event_limit=2)
            self.assertTrue(limited["metrics"]["trace_truncated"])
            self.assertEqual(limited["output"], state)
            for k in counts:
                self.assertEqual(limited["metrics"][k], counts[k])

    def test_known_counts_and_quick3_improvement(self):
        for name in ("merge", "quick", "heap", "insertion", "selection"):
            self.assertEqual(run_sort([2, 1], name)["metrics"]["comparisons"], 1)
        self.assertEqual(run_sort(list(range(10)), "quick")["metrics"]["comparisons"], 45)
        # Quick3 must beat standard Quick on sorted and equal arrays
        q1_sorted = run_sort(list(range(100)), "quick")["metrics"]["comparisons"]
        q3_sorted = run_sort(list(range(100)), "quick3")["metrics"]["comparisons"]
        self.assertLess(q3_sorted, q1_sorted // 3)
        q1_equal = run_sort([7] * 100, "quick")["metrics"]["comparisons"]
        q3_equal = run_sort([7] * 100, "quick3")["metrics"]["comparisons"]
        self.assertLess(q3_equal, q1_equal // 10)

    def test_large_adversarial_quick(self):
        for a in [list(range(1500)), list(range(1500, 0, -1)), [7] * 1500]:
            b = a[:]
            ALGORITHMS["quick"](a)
            ALGORITHMS["quick3"](b)
            self.assertEqual(a, sorted(a))
            self.assertEqual(b, sorted(b))

    def test_invalid(self):
        with self.assertRaises(ValueError):
            run_sort([1], "unknown")
        with self.assertRaises(ValueError):
            run_sort([float("nan")], "merge")
