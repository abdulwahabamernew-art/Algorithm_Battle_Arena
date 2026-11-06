---
title: Algorithm Battle Arena
emoji: ⚔️
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 5.49.1
app_file: app.py
pinned: false
license: mit
short_description: Interactive CS Lab for Sorting, Searching, Graphs & Big-O
---

# ⚔️ Algorithm Battle Arena v1.0 — ساحة معارك الخوارزميات

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Gradio 5.49.1](https://img.shields.io/badge/Gradio-5.49.1-FF7C00?logo=gradio&logoColor=white)](https://www.gradio.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e.svg)](LICENSE)
[![Zero Core Dependencies](https://img.shields.io/badge/Core-Zero_Dependencies-38bdf8)]()

**Algorithm Battle Arena** is an academic-grade, interactive Computer Science laboratory and empirical benchmarking suite designed to bridge the gap between **theoretical asymptotic complexity ($O, \Theta, \Omega$)** and **real-world empirical execution behavior**.

يمثل مشروع **Algorithm Battle Arena (الإصدار v1.0.0)** مختبراً تعليمياً وبحثياً متكاملاً لتحليل وتصميم الخوارزميات، يربط بين **التحليل الرياضي النظري (Big-O)** و**التجربة المعيارية المحكومة (Controlled Benchmarking)** عبر 6 مختبرات تفاعلية باللغتين العربية والإنجليزية.

* **Prepared by / إعداد الطالب:** Abdulwahab Yahya Mohammed Amer (عبدالوهاب يحيى محمد عامر)
* **Theoretical Supervision / الإشراف النظري:** Dr. Moath Al-Sabri (د. معاذ الصبري)
* **Practical Supervision / الإشراف العملي:** Eng. Mohammed Al-Wassabi (م. محمد الوصابي)

## 🌟 Key Features & Laboratories | المختبرات والمزايا الأساسية

1. **01 · Sorting Visualizer (مختبر محاكاة الترتيب خطوة بخطوة):**
   * Supports **6 sorting algorithms**: `Merge Sort`, `Quick Sort (Lomuto Last Pivot)`, `Quick Sort (3-Way Dutch National Flag + Median-of-3)`, `Heap Sort`, `Insertion Sort`, and `Selection Sort`.
   * **Visual Stability Tracking:** Automatically tags duplicate elements (e.g., `3(أ)`, `3(ب)`) so students can visually verify whether relative order is preserved.
   * **Live Auxiliary Buffer View:** Displays `Left` and `Right` temporary merge buffers in real time during `Merge Sort`.
2. **02 · Sorting Benchmark Arena (ساحة المقارنة المعيارية العادلة):**
   * Isolates `time.perf_counter_ns()` timing from tracing overhead (`recorder=None`), performs warmup runs, shuffles execution order per repeat (`rng.shuffle`), and reports median and min–max range across 9 repeats.
   * **Fair Memory & Write Accounting:** Separates in-place array writes (`writes`) from auxiliary buffer copies (`aux_writes`), reporting `total_writes` and peak auxiliary memory (`max_aux_space`).
3. **03 · Asymptotic Scaling & Doubling Ratio Lab (مختبر النمو التقاربي ورتب Big-O):**
   * Runs automated multi-size sweeps across doubling sizes ($n, 2n, 4n, 8n$) and computes the empirical **Doubling Ratio** $R = rac{C(2n)}{C(n)}$ to prove $\Theta(n)$ ($R pprox 2.0$), $\Theta(n \log n)$ ($R pprox 2.1	ext{–}2.3$), and $\Theta(n^2)$ ($R pprox 4.0$).
4. **04 · Searching Arena (ساحة خوارزميات البحث):**
   * Step-by-step visual probing and benchmarking for `Linear Search` ($O(n)$), `Binary Search` ($O(\log n)$), `Jump Search` ($O(\sqrt{n})$), and `Interpolation Search` ($O(\log \log n)$).
5. **05 · Graph Pathfinding Arena (ساحة المسارات الشبكية):**
   * Visual 2D grid battle comparing `BFS`, `DFS`, `Dijkstra`, and `A* (Manhattan Heuristic)` across mazes and weighted terrains (`cost=1` vs `cost=3`), comparing explored nodes (`visited_count`), step length, and total weighted path cost.
6. **06 · Smart Algorithm Advisor & Interactive Quiz (المستشار الذكي وبنك الأسئلة):**
   * Automatically profiles any dataset's **Inversion Ratio (Pre-sortedness)** and **Duplicate Ratio**, applies user constraints (Stability / Strict $O(1)$ Memory), recommends the optimal algorithm, and validates it with a live benchmark + an interactive self-assessment quiz.

## 📊 Theoretical & Empirical Matrix | مصفوفة التعقيد الخوارزمي

| Algorithm | Best Time | Average Time | Worst Time | Auxiliary Space | Stable? | Key Engineering Insight |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Merge Sort** | $\Theta(n \log n)$ | $\Theta(n \log n)$ | $\Theta(n \log n)$ | $O(n)$ | Yes ✓ | Guaranteed $\Theta(n \log n)$ & stable, but requires $O(n)$ buffer copies (`aux_writes`). |
| **Quick Sort (Last Pivot)** | $\Theta(n \log n)$ | $\Theta(n \log n)$ | $\Theta(n^2)$ | $O(\log n)$ | No ✗ | Fast cache locality on random data, but degrades to $\Theta(n^2)$ on sorted/equal data. |
| **Quick Sort (3-Way Median-3)** | $\Theta(n)$ | $\Theta(n \log n)$ | $\Theta(n \log n)$* | $O(\log n)$ | No ✗ | Eliminates $\Theta(n^2)$ on sorted inputs via Median-of-3 and runs in $\Theta(n)$ on duplicates. |
| **Heap Sort** | $\Theta(n)$ / $\Theta(n \log n)$ | $\Theta(n \log n)$ | $\Theta(n \log n)$ | $O(1)$ | No ✗ | Strictly in-place $O(1)$ auxiliary space with worst-case $\Theta(n \log n)$ guarantee. |
| **Insertion Sort** | $\Theta(n)$ | $\Theta(n^2)$ | $\Theta(n^2)$ | $O(1)$ | Yes ✓ | Optimal $\Theta(n)$ on nearly-sorted or small arrays ($n \le 32$). |
| **Selection Sort** | $\Theta(n^2)$ | $\Theta(n^2)$ | $\Theta(n^2)$ | $O(1)$ | No ✗ | Always performs $n(n-1)/2$ comparisons, but at most $n-1$ swaps. |

## 🚀 Quickstart | طريقة التشغيل السريع

### 1. Run Interactive Web UI (Gradio / Hugging Face Spaces)
```bash
python -m pip install -r requirements.txt
python app.py
```

### 2. Run Offline Core & CLI (Zero External Dependencies)
```bash
# Run the complete unit test suite (19 tests across all 6 modules)
python -m unittest discover -s tests -v

# Run CLI benchmark & export JSON/CSV traces for all 6 sorting algorithms
python -m arena --values "8,3,5,1,3,-2" --all-algorithms --trace --output outputs/demo
```

## 📁 Repository Structure | هيكل المشروع

```text
Algorithm_Battle_Arena/
├── app.py                      # 6-Tab Gradio Interactive Dashboard (Hugging Face entry point)
├── requirements.txt            # Gradio dependency for web UI
├── pyproject.toml              # Standard Python packaging metadata
├── arena/
│   ├── core.py                 # Validation, Recorder contract, memory & write counters
│   ├── sorting.py              # 6 Sorting algorithms + duplicate stability tagger
│   ├── searching.py            # 4 Searching algorithms + visual step renderer
│   ├── graphs.py               # 4 Graph pathfinding algorithms (BFS, DFS, Dijkstra, A*)
│   ├── advisor.py              # Dataset statistical profiler, Smart Advisor & Quiz
│   ├── benchmark.py            # Isolated perf_counter_ns benchmarking harness
│   ├── analysis.py             # Multi-pattern & Asymptotic Scaling (Doubling Ratio) reports
│   ├── ui_helpers.py           # SVG bar renderer, merge buffer & stability replay
│   └── __main__.py             # Offline CLI entry point
├── tests/                      # 18 automated unit tests covering all arenas
├── docs/                       # Detailed Arabic methodology, scope & metrics docs
└── examples/demo/              # Sample exported JSON traces and CSV benchmarks
```
