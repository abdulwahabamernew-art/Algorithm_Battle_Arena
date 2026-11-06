"""Run from project root: python -m arena --values '8,3,5,1' --trace."""
import argparse
import csv
import json
from pathlib import Path
import random
from .benchmark import benchmark
from .sorting import ALGORITHMS, CORE_ALGORITHMS, run_sort


def main():
    parser = argparse.ArgumentParser(description="Algorithm Battle Arena CLI (offline)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--values", help="Comma-separated integers; empty string means []")
    group.add_argument("--size", type=int, default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--pattern",
        choices=["random", "sorted", "reversed", "equal", "nearly_sorted"],
        default="random",
    )
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--all-algorithms", action="store_true", help="Run all 6 sorting algorithms")
    parser.add_argument("--trace", action="store_true")
    parser.add_argument("--event-limit", type=int, default=20000)
    parser.add_argument("--output", default="outputs")
    args = parser.parse_args()

    if args.repeats < 1 or args.event_limit < 0:
        parser.error("Invalid repeats or event limit")
    if args.size is not None and args.size < 0:
        parser.error("size must be nonnegative")

    if args.values is not None:
        try:
            values = [] if not args.values.strip() else [int(x.strip()) for x in args.values.split(",")]
        except ValueError:
            parser.error("values must contain comma-separated integers")
    else:
        n = 20 if args.size is None else args.size
        rng = random.Random(args.seed)
        values = [rng.randint(-1000, 1000) for _ in range(n)]
        if args.pattern == "sorted":
            values.sort()
        elif args.pattern == "reversed":
            values.sort(reverse=True)
        elif args.pattern == "equal":
            values = [7] * n
        elif args.pattern == "nearly_sorted":
            values.sort()
            for _ in range(max(1, n // 20)):
                if n >= 2:
                    i = rng.randrange(n - 1)
                    values[i], values[i + 1] = values[i + 1], values[i]

    selected = list(ALGORITHMS) if args.all_algorithms else list(CORE_ALGORITHMS)
    report = benchmark(values, args.repeats, algorithms=selected)
    report["generation"] = dict(
        seed=args.seed, pattern=args.pattern if args.values is None else "manual"
    )
    folder = Path(args.output)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "benchmark.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    fields = [
        "algorithm",
        "n",
        "repeats",
        "comparisons",
        "swaps",
        "writes",
        "aux_writes",
        "total_writes",
        "max_aux_space",
        "median_ns",
        "min_ns",
        "max_ns",
    ]
    with (folder / "comparison.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(report["results"])
    for row in report["results"]:
        print(
            f"{row['algorithm']:10} comparisons={row['comparisons']:6} swaps={row['swaps']:6} "
            f"writes={row['writes']:6} total_writes={row['total_writes']:6} median={row['median_ns']/1e6:.6f} ms"
        )
    if args.trace:
        for name in selected:
            result = run_sort(values, name, event_limit=args.event_limit)
            (folder / f"{name}_trace.json").write_text(
                json.dumps(result, indent=2), encoding="utf-8"
            )
            if result["metrics"]["trace_truncated"]:
                print(f"{name}: trace truncated; counts and output are complete.")
    print("Saved to", folder.resolve())


if __name__ == "__main__":
    main()
