"""Timing excludes input copying, validation, tracing, counters and output I/O."""
import platform
import random
import statistics
import time
from .core import validate
from .sorting import ALGORITHMS, CORE_ALGORITHMS, run_sort


def benchmark(values, repeats=7, algorithms=None):
    if type(repeats) is not int or repeats < 1:
        raise ValueError("repeats must be a positive integer")
    data = validate(values)
    expected = sorted(data)
    selected = list(CORE_ALGORITHMS if algorithms is None else algorithms)
    if not selected or any(name not in ALGORITHMS for name in selected):
        raise ValueError("Invalid algorithm selection")

    samples = {name: [] for name in selected}
    for name in selected:
        warmup = data[:]
        ALGORITHMS[name](warmup)
        if warmup != expected:
            raise AssertionError(f"Warmup result is incorrect for {name}")

    rng = random.Random(42)
    for _ in range(repeats):
        order = selected[:]
        rng.shuffle(order)
        for name in order:
            working = data[:]
            start = time.perf_counter_ns()
            ALGORITHMS[name](working)
            elapsed = time.perf_counter_ns() - start
            if working != expected:
                raise AssertionError(f"Timed result is incorrect for {name}")
            samples[name].append(elapsed)

    rows = []
    for name in selected:
        measured = run_sort(data, name, trace=False)
        rows.append(
            dict(
                algorithm=name,
                n=len(data),
                repeats=repeats,
                median_ns=statistics.median(samples[name]),
                min_ns=min(samples[name]),
                max_ns=max(samples[name]),
                samples_ns=samples[name],
                **measured["metrics"],
            )
        )
    return dict(
        python=platform.python_version(),
        platform=platform.platform(),
        timer="perf_counter_ns",
        input=data,
        results=rows,
    )
