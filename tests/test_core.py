import unittest
from arena.core import Recorder, validate


class ContractTests(unittest.TestCase):
    def test_validation_and_copy(self):
        a = [2, -1, 2]
        self.assertEqual(validate(a), a)
        self.assertIsNot(validate(a), a)
        for value in [True, 2.5, "3", None]:
            with self.assertRaises(ValueError):
                validate([value])

    def test_counts_and_limit(self):
        r = Recorder(limit=2)
        a = [2, 1]
        self.assertFalse(r.compare(2, 1, 0, 1))
        r.swap(a, 0, 1)
        r.swap(a, 0, 0)
        r.write(a, 0, -2)
        r.record_aux(writes=4, space=6)
        self.assertEqual((r.comparisons, r.swaps, r.writes, r.aux_writes, r.max_aux_space), (1, 1, 3, 4, 6))
        self.assertEqual(r.summary()["total_writes"], 7)
        self.assertEqual(len(r.events), 2)
        self.assertTrue(r.summary()["trace_truncated"])
        self.assertEqual(a, [-2, 2])

    def test_disabled_trace(self):
        r = Recorder(enabled=False)
        r.compare(1, 2, 0, 1)
        self.assertEqual(r.events, [])
        self.assertEqual(r.comparisons, 1)
        self.assertFalse(r.summary()["trace_truncated"])
