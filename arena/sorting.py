"""Sorting algorithms supporting both instrumented tracing and uninstrumented benchmarking."""
from .core import Recorder, validate


ALGORITHM_META = {
    "merge": {
        "name": "Merge Sort",
        "ar_name": "الترتيب بالدمج (Merge Sort)",
        "best": "Θ(n log n)",
        "average": "Θ(n log n)",
        "worst": "Θ(n log n)",
        "space": "O(n)",
        "stable": True,
        "paradigm": "Divide & Conquer (تقسيم ودمج)",
    },
    "quick": {
        "name": "Quick Sort (Last Pivot)",
        "ar_name": "الترتيب السريع — محور أخير (Quick Sort)",
        "best": "Θ(n log n)",
        "average": "Θ(n log n)",
        "worst": "Θ(n²)",
        "space": "O(log n)",
        "stable": False,
        "paradigm": "Divide & Conquer — Lomuto Partition",
    },
    "quick3": {
        "name": "Quick Sort (3-Way Median-3)",
        "ar_name": "الترتيب السريع الثلاثي المحسّن (3-Way Quick Sort)",
        "best": "Θ(n)",
        "average": "Θ(n log n)",
        "worst": "Θ(n log n) عمليًا",
        "space": "O(log n)",
        "stable": False,
        "paradigm": "Divide & Conquer — Dutch National Flag + Median-of-3",
    },
    "heap": {
        "name": "Heap Sort",
        "ar_name": "الترتيب بالكومة (Heap Sort)",
        "best": "Θ(n) للمتساوي / Θ(n log n)",
        "average": "Θ(n log n)",
        "worst": "Θ(n log n)",
        "space": "O(1)",
        "stable": False,
        "paradigm": "Selection via Max-Heap (بنية الكومة)",
    },
    "insertion": {
        "name": "Insertion Sort",
        "ar_name": "الترتيب بالإدراج (Insertion Sort)",
        "best": "Θ(n)",
        "average": "Θ(n²)",
        "worst": "Θ(n²)",
        "space": "O(1)",
        "stable": True,
        "paradigm": "Incremental Insertion (بناء تدريجي مستقر)",
    },
    "selection": {
        "name": "Selection Sort",
        "ar_name": "الترتيب بالاختيار (Selection Sort)",
        "best": "Θ(n²)",
        "average": "Θ(n²)",
        "worst": "Θ(n²)",
        "space": "O(1)",
        "stable": False,
        "paradigm": "Incremental Selection (أقل عدد تبديلات O(n))",
    },
}


def merge_sort(a, r=None):
    def visit(lo, hi, depth):
        if hi - lo <= 1:
            return
        mid = (lo + hi) // 2
        if r:
            r.emit("divide", lo=lo, mid=mid, hi=hi)
        visit(lo, mid, depth + 1)
        visit(mid, hi, depth + 1)
        left, right = a[lo:mid], a[mid:hi]
        if r:
            r.record_aux(writes=len(left) + len(right), space=len(a) + depth)
            r.emit("merge", lo=lo, mid=mid, hi=hi, left=left[:], right=right[:])
        i = j = 0
        for k in range(lo, hi):
            take_left = j == len(right)
            if i < len(left) and j < len(right):
                take_left = (
                    r.compare(left[i], right[j], lo + i, mid + j, source="merge_buffers")
                    if r
                    else left[i] <= right[j]
                )
            if i < len(left) and take_left:
                value = left[i]
                src_idx = lo + i
                i += 1
            else:
                value = right[j]
                src_idx = mid + j
                j += 1
            if r:
                r.write(a, k, value, source_tag=src_idx)
            else:
                a[k] = value

    visit(0, len(a), 1)


def quick_sort(a, r=None):
    # Lomuto partition, last element pivot; explicit stack avoids recursion errors.
    if len(a) <= 1:
        return
    stack = [(0, len(a) - 1)]
    while stack:
        if r:
            r.record_aux(space=len(stack) * 2)
        lo, hi = stack.pop()
        if lo >= hi:
            continue
        pivot = a[hi]
        if r:
            r.emit("pivot", index=hi, value=pivot, lo=lo, hi=hi + 1)
        i = lo
        for j in range(lo, hi):
            less = r.compare(a[j], pivot, j, hi) if r else a[j] <= pivot
            if less:
                if r:
                    r.swap(a, i, j)
                elif i != j:
                    a[i], a[j] = a[j], a[i]
                i += 1
        if r:
            r.swap(a, i, hi)
        elif i != hi:
            a[i], a[hi] = a[hi], a[i]
        if r:
            r.emit("partition", lo=lo, hi=hi + 1, pivot_index=i)
        parts = [(lo, i - 1), (i + 1, hi)]
        parts.sort(key=lambda p: p[1] - p[0], reverse=True)
        stack.extend(p for p in parts if p[0] < p[1])


def quick3_sort(a, r=None):
    """3-Way Dutch National Flag Quick Sort with Median-of-Three pivot selection."""
    if len(a) <= 1:
        return
    stack = [(0, len(a) - 1)]
    while stack:
        if r:
            r.record_aux(space=len(stack) * 2)
        lo, hi = stack.pop()
        if lo >= hi:
            continue
        mid = (lo + hi) // 2
        # Median-of-three ordering on (lo, mid, hi)
        for x, y in ((lo, mid), (mid, hi), (lo, mid)):
            greater = r.compare(a[x], a[y], x, y, ">") if r else a[x] > a[y]
            if greater:
                if r:
                    r.swap(a, x, y)
                else:
                    a[x], a[y] = a[y], a[x]
        # Place median at lo to act as pivot for 3-way partition
        if r:
            r.swap(a, lo, mid)
        elif lo != mid:
            a[lo], a[mid] = a[mid], a[lo]
        pivot = a[lo]
        if r:
            r.emit("pivot", index=lo, value=pivot, lo=lo, hi=hi + 1)
        lt = lo
        gt = hi
        i = lo + 1
        while i <= gt:
            less = r.compare(a[i], pivot, i, lt, "<") if r else a[i] < pivot
            if less:
                if r:
                    r.swap(a, lt, i)
                elif lt != i:
                    a[lt], a[i] = a[i], a[lt]
                lt += 1
                i += 1
            else:
                greater = r.compare(a[i], pivot, i, lt, ">") if r else a[i] > pivot
                if greater:
                    if r:
                        r.swap(a, i, gt)
                    elif i != gt:
                        a[i], a[gt] = a[gt], a[i]
                    gt -= 1
                else:
                    i += 1
        if r:
            r.emit("partition", lo=lo, hi=hi + 1, pivot_index=lt, equal_end=gt)
        parts = [(lo, lt - 1), (gt + 1, hi)]
        parts.sort(key=lambda p: p[1] - p[0], reverse=True)
        stack.extend(p for p in parts if p[0] < p[1])


def heap_sort(a, r=None):
    def sift(root, end):
        if r:
            r.emit("heapify", root=root, heap_size=end)
        while 2 * root + 1 < end:
            largest = root
            for child in (2 * root + 1, 2 * root + 2):
                if child < end:
                    greater = (
                        r.compare(a[child], a[largest], child, largest, ">")
                        if r
                        else a[child] > a[largest]
                    )
                    if greater:
                        largest = child
            if largest == root:
                break
            if r:
                r.swap(a, root, largest)
            else:
                a[root], a[largest] = a[largest], a[root]
            root = largest

    for root in range(len(a) // 2 - 1, -1, -1):
        sift(root, len(a))
    for end in range(len(a) - 1, 0, -1):
        if r:
            r.swap(a, 0, end)
        else:
            a[0], a[end] = a[end], a[0]
        if r:
            r.emit("extract", sorted_index=end, heap_size=end)
        sift(0, end)


def insertion_sort(a, r=None):
    """Stable in-place Insertion Sort using adjacent swaps when traced or shifts when uninstrumented."""
    n = len(a)
    for i in range(1, n):
        if r:
            r.emit("pivot", index=i, value=a[i], lo=0, hi=i + 1)
            j = i
            while j > 0:
                # Strictly greater (a[j-1] > a[j]) preserves stability
                greater = r.compare(a[j - 1], a[j], j - 1, j, ">")
                if not greater:
                    break
                r.swap(a, j - 1, j)
                j -= 1
        else:
            key = a[i]
            j = i - 1
            while j >= 0 and a[j] > key:
                a[j + 1] = a[j]
                j -= 1
            a[j + 1] = key


def selection_sort(a, r=None):
    """In-place Selection Sort: Θ(n²) comparisons, at most n-1 swaps."""
    n = len(a)
    for i in range(n - 1):
        min_idx = i
        if r:
            r.emit("pivot", index=i, value=a[i], lo=i, hi=n)
        for j in range(i + 1, n):
            less = r.compare(a[j], a[min_idx], j, min_idx, "<") if r else a[j] < a[min_idx]
            if less:
                min_idx = j
        if min_idx != i:
            if r:
                r.swap(a, i, min_idx)
            else:
                a[i], a[min_idx] = a[min_idx], a[i]
        if r:
            r.emit("extract", sorted_index=i, heap_size=n - i)


ALGORITHMS = {
    "merge": merge_sort,
    "quick": quick_sort,
    "quick3": quick3_sort,
    "heap": heap_sort,
    "insertion": insertion_sort,
    "selection": selection_sort,
}

CORE_ALGORITHMS = ("merge", "quick", "heap")


def build_initial_tags(values):
    """Assign Arabic letter tags to duplicate values so students can track stability."""
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    letters = "أبجدهوزحطيكلمنسعفصقرشتثخذضظغ"
    seen = {}
    tags = []
    for v in values:
        if counts[v] > 1:
            idx = seen.get(v, 0)
            seen[v] = idx + 1
            suffix = letters[idx] if idx < len(letters) else str(idx + 1)
            tags.append(f"{v}({suffix})")
        else:
            tags.append(str(v))
    return tags


def run_sort(values, algorithm, trace=True, event_limit=20000):
    if algorithm not in ALGORITHMS:
        raise ValueError("Unknown algorithm: " + str(algorithm))
    a = validate(values)
    original = a[:]
    r = Recorder(enabled=trace, limit=event_limit)
    r.emit("start", array=a[:])
    ALGORITHMS[algorithm](a, r)
    r.emit("done", array=a[:])
    summary = r.summary()
    summary["stable_theoretical"] = ALGORITHM_META[algorithm]["stable"]
    return dict(
        schema_version=1,
        algorithm=algorithm,
        input=original,
        output=a,
        initial_tags=build_initial_tags(original),
        metrics=summary,
        events=r.events,
    )
