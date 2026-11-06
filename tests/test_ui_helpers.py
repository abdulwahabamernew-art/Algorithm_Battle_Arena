import unittest
from arena.ui_helpers import build_session, parse_values, replay_until, replay_with_tags, render_step


class UIHelperTests(unittest.TestCase):
    def test_parse_and_limits(self):
        self.assertEqual(parse_values("3, -1, 3"), [3, -1, 3])
        for invalid in ["", "1,x", ","]:
            with self.assertRaises(ValueError):
                parse_values(invalid)
        with self.assertRaises(ValueError):
            parse_values(",".join("1" for _ in range(81)))

    def test_replay_finishes_at_output_and_preserves_merge_stability(self):
        for name in [
            "Merge Sort",
            "Quick Sort (Last Pivot)",
            "Quick Sort (3-Way Median-3)",
            "Heap Sort",
            "Insertion Sort",
            "Selection Sort",
        ]:
            result = build_session("5,3,4,3,-2", name)
            state, _ = replay_until(result, len(result["events"]) - 1)
            self.assertEqual(state, result["output"])
            state2, tags, _, _ = replay_with_tags(result, len(result["events"]) - 1)
            self.assertEqual(state2, result["output"])
            if name in ("Merge Sort", "Insertion Sort"):
                # Stable sorts must preserve 3(أ) before 3(ب)
                dup_tags = [t for t in tags if t.startswith("3(")]
                self.assertEqual(dup_tags, ["3(أ)", "3(ب)"])
            html = render_step(result, 0)
            self.assertIn("الخطوة", html)
            self.assertIn("aba-chart", html)
