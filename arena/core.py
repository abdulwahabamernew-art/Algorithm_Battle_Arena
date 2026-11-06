"""Shared event contract and instrumentation recorder. Indices are zero-based; range ends are exclusive."""
from dataclasses import dataclass, field


def validate(values):
    data = list(values)
    if any(type(x) is not int for x in data):
        raise ValueError("Only integers are supported (no booleans).")
    return data


@dataclass
class Recorder:
    enabled: bool = True
    limit: int = 20000
    comparisons: int = 0
    swaps: int = 0
    writes: int = 0
    aux_writes: int = 0
    max_aux_space: int = 0
    total_events: int = 0
    events: list = field(default_factory=list)

    def __post_init__(self):
        if type(self.limit) is not int or self.limit < 0:
            raise ValueError("Event limit must be a nonnegative integer.")

    def emit(self, kind, **details):
        self.total_events += 1
        if self.enabled and len(self.events) < self.limit:
            self.events.append(dict(step=self.total_events, kind=kind, **details))

    def compare(self, left, right, i, j, operator="<=", source="array"):
        self.comparisons += 1
        if operator == "<=":
            result = left <= right
        elif operator == "<":
            result = left < right
        elif operator == ">":
            result = left > right
        elif operator == "==":
            result = left == right
        else:
            raise ValueError(f"Unsupported operator: {operator}")
        self.emit(
            "compare",
            indices=[i, j],
            values=[left, right],
            operator=operator,
            result=result,
            source=source,
        )
        return result

    def swap(self, a, i, j):
        if i == j:
            return  # A self-swap is not counted as a data movement.
        a[i], a[j] = a[j], a[i]
        self.swaps += 1
        self.writes += 2
        self.emit("swap", indices=[i, j], values=[a[i], a[j]])

    def write(self, a, i, value, source_tag=None):
        a[i] = value
        self.writes += 1
        payload = dict(index=i, value=value)
        if source_tag is not None:
            payload["source_tag"] = source_tag
        self.emit("write", **payload)

    def record_aux(self, writes=0, space=0):
        if writes > 0:
            self.aux_writes += int(writes)
        if space > self.max_aux_space:
            self.max_aux_space = int(space)

    def summary(self):
        return dict(
            comparisons=self.comparisons,
            swaps=self.swaps,
            writes=self.writes,
            aux_writes=self.aux_writes,
            total_writes=self.writes + self.aux_writes,
            max_aux_space=self.max_aux_space,
            total_events=self.total_events,
            recorded_events=len(self.events),
            trace_truncated=self.enabled and self.total_events > len(self.events),
        )
