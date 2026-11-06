# Contributing

Thank you for helping improve Algorithm Battle Arena.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Before opening a pull request

Run the tests and compile check:

```bash
python -m unittest discover -s tests -v
python -m compileall -q arena app.py
```

Changes to algorithm behavior should include tests and should explain any change to complexity, stability, memory, or instrumentation semantics. Benchmark claims should include the input pattern, seed, number of repeats, Python version, and hardware context.

Keep generated outputs, credentials, datasets, and model artifacts out of commits. Use small, focused pull requests with a clear description of the educational or engineering rationale.
