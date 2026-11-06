import unittest
from arena.analysis import (
    PATTERNS,
    compare,
    compare_scaling,
    dataset,
    render_report,
    render_scaling_report,
)
from arena.ui_helpers import build_session, replay_until, render_step


class ComparisonTests(unittest.TestCase):
    def test_every_algorithm_receives_same_input(self):
        for pattern in PATTERNS:
            values = dataset(40, pattern, 42)
            report = compare([], "بيانات مولدة", 40, pattern, 42, repeats=2)
            self.assertEqual(values, report["input"])
            self.assertEqual(len(report["results"]), 3)
            self.assertTrue(
                all(
                    row["n"] == 40 and len(row["samples_ns"]) == 2
                    for row in report["results"]
                )
            )
            html = render_report(report)
            self.assertIn("المقارنات", html)
            self.assertIn("زمن التنفيذ", html)
            self.assertIn("الكتابات", html)
            self.assertIn("التعقيد المتوقع", html)

    def test_sorted_quick_worst_case_and_manual_validation(self):
        report = compare([], "بيانات مولدة", 40, "مرتب تصاعديًا", 1, repeats=1)
        quick = next(row for row in report["results"] if row["algorithm"] == "quick")
        self.assertEqual(quick["comparisons"], 40 * 39 // 2)
        self.assertIn("O(n²)", render_report(report))
        manual = compare([3, -1, 3], "المصفوفة المدخلة", 40, "عشوائي", 9, repeats=1)
        self.assertEqual(manual["input"], [3, -1, 3])
        with self.assertRaises(ValueError):
            dataset(1201, "عشوائي", 42)

    def test_signed_visual_and_replay(self):
        result = build_session("-5,0,4,-1", "Heap Sort")
        html = render_step(result, 0)
        self.assertIn("−5", html)
        self.assertIn("<svg", html)
        self.assertIn("فوق الخط = موجب، تحته = سالب", html)
        final, _ = replay_until(result, len(result["events"]) - 1)
        self.assertEqual(final, result["output"])

    def test_scaling_sweep_and_report(self):
        sc = compare_scaling("مرتب تصاعديًا", 42, base_size=20, steps=3, repeats=1)
        self.assertEqual(sc["sizes"], [20, 40, 80])
        html = render_scaling_report(sc)
        self.assertIn("Doubling Ratio", html)
        self.assertIn("<polyline", html)
