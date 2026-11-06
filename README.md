# Algorithm Battle Arena

[![CI](https://github.com/abdulwahabamernew-art/Algorithm_Battle_Arena/actions/workflows/ci.yml/badge.svg)](https://github.com/abdulwahabamernew-art/Algorithm_Battle_Arena/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e.svg)](LICENSE)

**Algorithm Battle Arena** is an interactive computer-science laboratory for connecting asymptotic analysis with controlled empirical experiments. It provides visual demonstrations, reproducible benchmarks, graph pathfinding comparisons, and a rule-based algorithm advisor in Arabic and English.

**بالعربية:** [اقرأ README العربي](README_AR.md)

## Scope

The project contains six educational laboratories:

1. Sorting visualization for Merge, Quick, 3-way Quick, Heap, Insertion, and Selection Sort.
2. Controlled sorting benchmarks with warm-up runs, randomized execution order, median timing, write accounting, and auxiliary-space metrics.
3. Empirical scaling experiments using doubling ratios.
4. Linear, Binary, Jump, and Interpolation Search comparisons.
5. BFS, DFS, Dijkstra, and A* pathfinding on weighted grids.
6. A data profiler, algorithm advisor, and interactive quiz.

The project is educational and empirical: measured runtime depends on hardware, Python version, input distribution, and benchmark settings. Experimental results must not be interpreted as universal theoretical proofs.

## Complexity summary

| Algorithm | Best | Average | Worst | Extra space | Stable |
|---|---:|---:|---:|---:|:---:|
| Merge Sort | Θ(n log n) | Θ(n log n) | Θ(n log n) | O(n) | Yes |
| Quick Sort (last pivot) | Θ(n log n) | Θ(n log n) | Θ(n²) | O(log n) | No |
| Quick Sort (3-way, median-of-three) | Θ(n) on duplicates | Θ(n log n) | Θ(n log n)* | O(log n) | No |
| Heap Sort | Θ(n log n) | Θ(n log n) | Θ(n log n) | O(1) | No |
| Insertion Sort | Θ(n) | Θ(n²) | Θ(n²) | O(1) | Yes |
| Selection Sort | Θ(n²) | Θ(n²) | Θ(n²) | O(1) | No |

\* Subject to the implementation's pivot and recursion behavior.

## Quick start

### Interactive dashboard

```bash
python -m venv .venv
source .venv/bin/activate              # Windows: .venv\\Scripts\\activate
python -m pip install -e .
python app.py
```

### Offline CLI and tests

```bash
python -m unittest discover -s tests -v
python -m arena --values "8,3,5,1,3,-2" --all-algorithms --trace --output outputs/demo
```

## Repository layout

```text
app.py                  # Gradio dashboard entry point
arena/                  # Offline algorithms, metrics, benchmark, advisor, and CLI
tests/                  # 19 tests across 6 test modules
docs/                   # Arabic scope and metrics documentation
examples/demo/          # Small, reviewable example outputs
pyproject.toml          # Package metadata and dependencies
```

## Reproducibility and responsible interpretation

Benchmarks use isolated timing, warm-up runs, seeded input generation where applicable, and explicit counters for comparisons, swaps, writes, auxiliary writes, and peak auxiliary space. For meaningful comparisons, record Python version, operating system, hardware, input pattern, seed, number of repeats, and commit hash.

## Development

```bash
python -m unittest discover -s tests -v
python -m compileall -q arena app.py
```

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. Academic reuse and citation guidance is available in [CITATION.cff](CITATION.cff).

## Acknowledgements

The project was prepared by Abdulwahab Yahya Mohammed Amer, with theoretical supervision by Dr. Moath Al-Sabri and practical supervision by Eng. Mohammed Al-Wassabi.

## License

The source code is released under the MIT License. See [LICENSE](LICENSE).
