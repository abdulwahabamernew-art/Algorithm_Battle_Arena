import unittest
from arena.advisor import QUIZ_QUESTIONS, advise_algorithm, grade_quiz, profile_dataset
from arena.graphs import compare_pathfinding, generate_grid, render_pathfinding_battle, run_pathfinding
from arena.searching import SEARCH_ALGORITHMS, benchmark_search, render_search_report, render_search_step, run_search


class NewArenasTests(unittest.TestCase):
    def test_searching_algorithms(self):
        arr = [-15, -4, 0, 3, 9, 12, 18, 25, 40]
        for alg in SEARCH_ALGORITHMS:
            hit = run_search(arr, 12, alg)
            self.assertTrue(hit["found"])
            self.assertEqual(arr[hit["found_index"]], 12)
            miss = run_search(arr, 11, alg)
            self.assertFalse(miss["found"])
            self.assertEqual(miss["found_index"], -1)
        bench = benchmark_search(arr, 18, repeats=2)
        self.assertEqual(len(bench["results"]), 4)
        self.assertIn("Search Arena", render_search_report(bench))
        self.assertIn("<svg", render_search_step(run_search(arr, 9, "binary"), 1))

    def test_graph_pathfinding(self):
        spec = generate_grid(rows=8, cols=10, preset="مفتوحة بلا عوائق", seed=7)
        bfs = run_pathfinding(spec, "bfs")
        astar = run_pathfinding(spec, "astar")
        dijkstra = run_pathfinding(spec, "dijkstra")
        self.assertTrue(bfs["found"] and astar["found"] and dijkstra["found"])
        self.assertEqual(bfs["path_cost"], astar["path_cost"])
        self.assertEqual(dijkstra["path_cost"], astar["path_cost"])
        self.assertLessEqual(astar["visited_count"], dijkstra["visited_count"])
        battle = compare_pathfinding("تضاريس موزونة (تكلفة متغيرة)", 42)
        self.assertIn("<svg", render_pathfinding_battle(battle))

    def test_advisor_and_quiz(self):
        prof = profile_dataset([1, 2, 3, 4, 5, 6])
        self.assertTrue(prof["is_sorted"])
        self.assertEqual(prof["inversion_ratio"], 0.0)
        adv_stable_inplace = advise_algorithm([4, 2, 1, 3], need_stable=True, strict_memory=True)
        self.assertEqual(adv_stable_inplace["recommended"], "insertion")
        adv_stable_large = advise_algorithm(list(range(100, 0, -1)), need_stable=True, strict_memory=False)
        self.assertEqual(adv_stable_large["recommended"], "merge")
        perfect_answers = [q["options"][q["correct"]] for q in QUIZ_QUESTIONS]
        html = grade_quiz(*perfect_answers)
        self.assertIn("100%", html)
