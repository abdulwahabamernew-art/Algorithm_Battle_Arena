"""Searching Arena: Linear, Binary, Jump, and Interpolation Search with step tracing."""
import math
import statistics
import time
from html import escape

from .core import Recorder, validate


SEARCH_META = {
    "linear": {
        "name": "Linear Search",
        "ar_name": "البحث الخطي (Linear Search)",
        "best": "Θ(1)",
        "average": "Θ(n)",
        "worst": "Θ(n)",
        "space": "O(1)",
        "requires_sorted": False,
        "color": "#fb923c",
    },
    "binary": {
        "name": "Binary Search",
        "ar_name": "البحث الثنائي (Binary Search)",
        "best": "Θ(1)",
        "average": "Θ(log n)",
        "worst": "Θ(log n)",
        "space": "O(1)",
        "requires_sorted": True,
        "color": "#38bdf8",
    },
    "jump": {
        "name": "Jump Search",
        "ar_name": "البحث بالقفز (Jump Search)",
        "best": "Θ(1)",
        "average": "Θ(√n)",
        "worst": "Θ(√n)",
        "space": "O(1)",
        "requires_sorted": True,
        "color": "#a78bfa",
    },
    "interpolation": {
        "name": "Interpolation Search",
        "ar_name": "البحث بالاستيفاء (Interpolation Search)",
        "best": "Θ(1)",
        "average": "Θ(log log n) للمنتظم",
        "worst": "Θ(n) للمنحرف",
        "space": "O(1)",
        "requires_sorted": True,
        "color": "#34d399",
    },
}


def linear_search(a, target, r=None):
    for i, val in enumerate(a):
        if r:
            r.emit("probe", index=i, value=val, target=target, lo=0, hi=len(a))
            eq = r.compare(val, target, i, i, "==")
        else:
            eq = val == target
        if eq:
            if r:
                r.emit("found", index=i, value=val)
            return i
    if r:
        r.emit("not_found", target=target)
    return -1


def binary_search(a, target, r=None):
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if r:
            r.emit("probe", index=mid, value=a[mid], target=target, lo=lo, hi=hi + 1)
            eq = r.compare(a[mid], target, mid, mid, "==")
        else:
            eq = a[mid] == target
        if eq:
            if r:
                r.emit("found", index=mid, value=a[mid])
            return mid
        less = r.compare(a[mid], target, mid, mid, "<") if r else a[mid] < target
        if less:
            lo = mid + 1
        else:
            hi = mid - 1
    if r:
        r.emit("not_found", target=target)
    return -1


def jump_search(a, target, r=None):
    n = len(a)
    if n == 0:
        if r:
            r.emit("not_found", target=target)
        return -1
    step = max(1, int(math.isqrt(n)))
    prev = 0
    while prev < n:
        bound = min(prev + step, n) - 1
        if r:
            r.emit("probe", index=bound, value=a[bound], target=target, lo=prev, hi=bound + 1)
            ge = not r.compare(a[bound], target, bound, bound, "<")
        else:
            ge = a[bound] >= target
        if ge:
            break
        prev += step
    if prev >= n:
        if r:
            r.emit("not_found", target=target)
        return -1
    end = min(prev + step, n)
    for i in range(prev, end):
        if r:
            r.emit("probe", index=i, value=a[i], target=target, lo=prev, hi=end)
            eq = r.compare(a[i], target, i, i, "==")
        else:
            eq = a[i] == target
        if eq:
            if r:
                r.emit("found", index=i, value=a[i])
            return i
    if r:
        r.emit("not_found", target=target)
    return -1


def interpolation_search(a, target, r=None):
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        if a[lo] == a[hi]:
            if r:
                r.emit("probe", index=lo, value=a[lo], target=target, lo=lo, hi=hi + 1)
                eq = r.compare(a[lo], target, lo, lo, "==")
            else:
                eq = a[lo] == target
            if eq:
                if r:
                    r.emit("found", index=lo, value=a[lo])
                return lo
            break
        if r:
            low_check = r.compare(target, a[lo], lo, lo, "<")
            high_check = r.compare(target, a[hi], hi, hi, ">") if not low_check else False
        else:
            low_check = target < a[lo]
            high_check = target > a[hi] if not low_check else False
        if low_check or high_check:
            break
        pos = lo + ((target - a[lo]) * (hi - lo)) // (a[hi] - a[lo])
        pos = max(lo, min(hi, pos))
        if r:
            r.emit("probe", index=pos, value=a[pos], target=target, lo=lo, hi=hi + 1)
            eq = r.compare(a[pos], target, pos, pos, "==")
        else:
            eq = a[pos] == target
        if eq:
            if r:
                r.emit("found", index=pos, value=a[pos])
            return pos
        less = r.compare(a[pos], target, pos, pos, "<") if r else a[pos] < target
        if less:
            lo = pos + 1
        else:
            hi = pos - 1
    if r:
        r.emit("not_found", target=target)
    return -1


SEARCH_ALGORITHMS = {
    "linear": linear_search,
    "binary": binary_search,
    "jump": jump_search,
    "interpolation": interpolation_search,
}


def run_search(values, target, algorithm="binary", trace=True, event_limit=5000):
    if algorithm not in SEARCH_ALGORITHMS:
        raise ValueError(f"Unknown search algorithm: {algorithm}")
    if type(target) is not int:
        raise ValueError("Target must be an integer")
    data = validate(values)
    working = sorted(data) if SEARCH_META[algorithm]["requires_sorted"] else data[:]
    r = Recorder(enabled=trace, limit=event_limit)
    r.emit("start", array=working[:], target=target)
    index = SEARCH_ALGORITHMS[algorithm](working, target, r)
    r.emit("done", array=working[:], found_index=index, target=target)
    probes = sum(1 for e in r.events if e["kind"] == "probe")
    metrics = r.summary()
    metrics["probes"] = probes
    return dict(
        schema_version=1,
        algorithm=algorithm,
        input=working,
        target=target,
        found_index=index,
        found=index != -1,
        metrics=metrics,
        events=r.events,
    )


def benchmark_search(values, target, repeats=9):
    data = sorted(validate(values))
    target = int(target)
    rows = []
    for name, fn in SEARCH_ALGORITHMS.items():
        samples = []
        for _ in range(repeats):
            start = time.perf_counter_ns()
            idx = fn(data, target, None)
            elapsed = time.perf_counter_ns() - start
            samples.append(elapsed)
        traced = run_search(data, target, name, trace=True)
        rows.append(
            dict(
                algorithm=name,
                n=len(data),
                target=target,
                found=traced["found"],
                found_index=idx,
                probes=traced["metrics"]["probes"],
                comparisons=traced["metrics"]["comparisons"],
                median_ns=statistics.median(samples),
                min_ns=min(samples),
                max_ns=max(samples),
            )
        )
    return dict(input=data, target=target, repeats=repeats, results=rows)


def render_search_step(result, step_index):
    state = result["input"]
    events = result["events"]
    index = 0 if not events else max(0, min(int(step_index), len(events) - 1))
    event = events[index] if events else None
    probed_history = {e["index"] for e in events[: index + 1] if e["kind"] == "probe"}
    current_probe = event.get("index") if event and event["kind"] in {"probe", "found"} else None
    found_idx = event.get("index") if event and event["kind"] == "found" else (
        event.get("found_index") if event and event["kind"] == "done" and event.get("found_index", -1) >= 0 else None
    )
    muted = set()
    if event and "lo" in event and "hi" in event:
        muted = set(range(len(state))) - set(range(event["lo"], event["hi"]))

    scale = max((abs(v) for v in state), default=1) or 1
    width = max(560, 80 + 48 * len(state))
    zero_y, amplitude = 143, 99
    bars = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 300" width="{width}" height="300">',
        f'<line x1="40" y1="{zero_y}" x2="{width-8}" y2="{zero_y}" stroke="#94a3b8" stroke-width="2"/>',
    ]
    for i, value in enumerate(state):
        height = max(4, round(amplitude * abs(value) / scale))
        top = zero_y - height if value >= 0 else zero_y
        x = 47 + 48 * i
        color = "#38bdf8"
        if i in probed_history:
            color = "#a78bfa"
        if i == current_probe:
            color = "#f97316"
        if i == found_idx:
            color = "#22c55e"
        opacity = "0.30" if i in muted else "1"
        label_y = max(16, top - 7) if value >= 0 else min(265, zero_y + height + 16)
        bars.append(
            f'<g opacity="{opacity}"><rect x="{x}" y="{top}" width="30" height="{height}" rx="4" fill="{color}"/>'
            f'<text x="{x+15}" y="{label_y}" text-anchor="middle" fill="#f8fafc" font-size="13">{value}</text>'
            f'<text x="{x+15}" y="288" text-anchor="middle" fill="#94a3b8" font-size="12">{i}</text></g>'
        )
    bars.append("</svg>")

    kind = event["kind"] if event else "start"
    if kind == "probe":
        desc = f"فحص الفهرس {event['index']} (القيمة {event['value']}) بحثًا عن الهدف {result['target']} ضمن المجال [{event['lo']}..{event['hi']-1}]"
    elif kind == "found":
        desc = f"✅ تم العثور على القيمة {result['target']} في الفهرس {event['index']}!"
    elif kind == "not_found":
        desc = f"❌ القيمة {result['target']} غير موجودة في المصفوفة."
    elif kind == "done":
        desc = f"انتهى البحث — النتيجة: {'موجود عند الفهرس ' + str(result['found_index']) if result['found'] else 'غير موجود'}."
    else:
        desc = f"بدء البحث عن الهدف {result['target']} في مصفوفة بحجم {len(state)} عنصر."

    meta = SEARCH_META[result["algorithm"]]
    return f"""<div dir="rtl" class="aba-card">
      <div class="aba-sim-top"><span class="aba-kicker">محاكاة البحث خطوة بخطوة · الهدف: {result['target']}</span>
      <span class="aba-count">الخطوة {index + 1} / {len(events)}</span></div>
      <h2>{escape(meta['ar_name'])}</h2>
      <div class="aba-event"><b>الحدث الحالي:</b> <span>{escape(desc)}</span></div>
      <div class="aba-chart" dir="ltr">{''.join(bars)}</div>
      <div class="aba-legend">
        <span><i style="background:#38bdf8"></i>عنصر ضمن المجال</span>
        <span><i style="background:#f97316"></i>فحص حالي (Probe)</span>
        <span><i style="background:#a78bfa"></i>تم فحصه سابقًا</span>
        <span><i style="background:#22c55e"></i>الهدف مطابق</span>
      </div>
      <div class="aba-progress">
        <span>إجمالي الفحوصات (Probes): {result['metrics']['probes']} · المقارنات: {result['metrics']['comparisons']}</span>
        <span>التعقيد النظري: متوسط {meta['average']} | أسوأ حالة {meta['worst']}</span>
      </div>
    </div>"""


def render_search_report(report):
    rows = report["results"]
    n = len(report["input"])
    target = report["target"]
    found_any = any(r["found"] for r in rows)
    best_probes = min(rows, key=lambda r: r["probes"])
    fastest = min(rows, key=lambda r: r["median_ns"])
    parts = [
        f'<div class="aba-report" dir="rtl"><header class="aba-report-head">'
        f'<span class="aba-kicker">مقارنة خوارزميات البحث على مصفوفة مرتبة</span>'
        f'<h2>تقرير ساحة البحث (Search Arena)</h2>'
        f'<p>حجم المصفوفة: {n:,} عنصر | الهدف المطلوب: <b>{target}</b> | '
        f'الحالة: {"تم العثور على الهدف" if found_any else "الهدف غير موجود (اختبار أسوأ حالة)"}</p></header>',
        '<div class="aba-stat-grid">',
        f'<div class="aba-stat"><small>أقل عدد فحوصات (Probes)</small>'
        f'<strong>{escape(SEARCH_META[best_probes["algorithm"]]["name"])}</strong>'
        f'<span>{best_probes["probes"]} فحص فقط</span></div>',
        f'<div class="aba-stat"><small>أسرع زمن وسيط</small>'
        f'<strong>{escape(SEARCH_META[fastest["algorithm"]]["name"])}</strong>'
        f'<span>{fastest["median_ns"] / 1e3:.2f} µs</span></div>',
        f'<div class="aba-stat"><small>الفارق النظري</small>'
        f'<strong>O(log n) vs O(n)</strong>'
        f'<span>البحث الثنائي يختصر المجال للنصف في كل خطوة</span></div>',
        '</div>',
        '<section class="aba-panel"><h3>جدول مقارنة خوارزميات البحث</h3>'
        '<div class="aba-table-wrap"><table class="aba-table"><thead><tr>'
        '<th>الخوارزمية</th><th>الفحوصات (Probes)</th><th>المقارنات</th>'
        '<th>النتيجة (الفهرس)</th><th>وسيط الزمن (µs)</th><th>متوسط التعقيد</th></tr></thead><tbody>',
    ]
    for r in rows:
        meta = SEARCH_META[r["algorithm"]]
        parts.append(
            f'<tr><th>{escape(meta["ar_name"])}</th>'
            f'<td dir="ltr">{r["probes"]:,}</td>'
            f'<td dir="ltr">{r["comparisons"]:,}</td>'
            f'<td dir="ltr">{r["found_index"] if r["found"] else "غير موجود (-1)"}</td>'
            f'<td dir="ltr">{r["median_ns"] / 1e3:.3f}</td>'
            f'<td dir="ltr">{escape(meta["average"])}</td></tr>'
        )
    parts.append("</tbody></table></div></section></div>")
    return "".join(parts)
