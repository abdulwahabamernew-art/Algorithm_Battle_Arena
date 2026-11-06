"""Fair, repeatable sorting comparison, asymptotic scaling sweep, and Arabic HTML reports."""
import random
from html import escape

from .benchmark import benchmark
from .core import validate
from .sorting import ALGORITHM_META, ALGORITHMS, CORE_ALGORITHMS


NAMES = {k: v["name"] for k, v in ALGORITHM_META.items()}
COLORS = {
    "merge": "#38bdf8",
    "quick": "#fb923c",
    "quick3": "#22c55e",
    "heap": "#a78bfa",
    "insertion": "#f43f5e",
    "selection": "#eab308",
}
PATTERNS = ("عشوائي", "مرتب تصاعديًا", "مرتب تنازليًا", "قيم متساوية", "شبه مرتب")


def dataset(size, pattern, seed):
    if type(size) is not int or not 1 <= size <= 1200:
        raise ValueError("حجم التجربة يجب أن يكون من 1 إلى 1200")
    if pattern not in PATTERNS:
        raise ValueError("نمط البيانات غير معروف")
    if type(seed) is not int:
        raise ValueError("البذرة يجب أن تكون عددًا صحيحًا")
    rng = random.Random(seed)
    values = [rng.randint(-10000, 10000) for _ in range(size)]
    if pattern == "مرتب تصاعديًا":
        values.sort()
    elif pattern == "مرتب تنازليًا":
        values.sort(reverse=True)
    elif pattern == "قيم متساوية":
        values = [7] * size
    elif pattern == "شبه مرتب":
        values.sort()
        swaps = max(1, size // 20)
        for _ in range(swaps):
            if size >= 2:
                i = rng.randrange(size - 1)
                values[i], values[i + 1] = values[i + 1], values[i]
    return values


def compare(values, source, size, pattern, seed, repeats=9, algorithms=None):
    """Return benchmark output with provenance; no tracing is included in timing."""
    if source == "المصفوفة المدخلة":
        data = validate(values)
        if not 1 <= len(data) <= 1200:
            raise ValueError("المصفوفة المدخلة يجب أن تحتوي من 1 إلى 1200 عنصر")
        origin = "المصفوفة المدخلة"
    elif source == "بيانات مولدة":
        data = dataset(int(size), pattern, int(seed))
        origin = f"{pattern} • بذرة {seed}"
    else:
        raise ValueError("مصدر البيانات غير معروف")
    report = benchmark(data, repeats, algorithms=algorithms)
    report["origin"] = origin
    return report


def _card(label, value, note):
    return (
        f'<div class="aba-stat"><small>{escape(label)}</small>'
        f'<strong>{escape(str(value))}</strong><span>{escape(note)}</span></div>'
    )


def _bars(rows, key, title, unit, digits=0):
    maximum = max((float(row[key]) for row in rows), default=0) or 1
    pieces = [
        f'<section class="aba-panel"><h3>{escape(title)}</h3>'
        '<p class="aba-hint">الأقل أفضل في هذا المقياس. لكل رسم مقياس أفقي مستقل.</p>'
    ]
    for row in rows:
        value = float(row[key])
        width = max(1, value / maximum * 100) if maximum > 0 else 1
        label = f"{value:,.{digits}f}"
        name = NAMES[row["algorithm"]]
        color = COLORS.get(row["algorithm"], "#38bdf8")
        pieces.append(
            f'<div class="aba-metric-row"><span>{escape(name)}</span>'
            f'<div class="aba-track" role="img" aria-label="{escape(name)}: {label} {escape(unit)}">'
            f'<div style="width:{width:.2f}%;background:{color}"></div></div>'
            f'<b dir="ltr">{label} {escape(unit)}</b></div>'
        )
    return "".join(pieces) + "</section>"


def render_report(report):
    rows = report["results"]
    n = len(report["input"])
    lowest_comparisons = min(rows, key=lambda r: r["comparisons"])
    lowest_writes = min(rows, key=lambda r: r["writes"])
    lowest_total_writes = min(rows, key=lambda r: r.get("total_writes", r["writes"]))
    fastest = min(rows, key=lambda r: r["median_ns"])
    repeated = rows[0]["repeats"]
    very_small = n < 100 or all(r["median_ns"] < 1_000_000 for r in rows)
    if n < 100:
        caveat = "هذه عينة صغيرة لتتبع الفكرة؛ للمقارنة الزمنية جرّب 300 عنصر أو أكثر."
    elif very_small:
        caveat = "الزمن أقل من 1 ms لبعض النتائج؛ قد يتأثر بضجيج البيئة. كرر التجربة بأحجام أكبر."
    else:
        caveat = "الأزمنة تخص هذا الجهاز وهذه المدخلات فقط؛ لا تثبت أن خوارزمية أسرع دائمًا."
    origin = escape(report.get("origin", "البيانات نفسها"))
    sample = ", ".join(str(v) for v in report["input"][:8])
    if n > 8:
        sample += ", …"
    parts = [
        f'<div class="aba-report" dir="rtl"><header class="aba-report-head">'
        f'<span class="aba-kicker">تجربة واحدة · نفس المدخلات لكل الخوارزميات</span>'
        f'<h2>تقرير المقارنة</h2><p>المصدر: {origin} | عدد العناصر: {n:,} | '
        f'تكرارات القياس: {repeated} | عينة: <span dir="ltr">[{escape(sample)}]</span></p></header>',
        '<div class="aba-stat-grid">',
        _card(
            "أقل مقارنات",
            NAMES[lowest_comparisons["algorithm"]],
            f'{lowest_comparisons["comparisons"]:,} مقارنة',
        ),
        _card(
            "أقل كتابات في القائمة",
            NAMES[lowest_writes["algorithm"]],
            f'{lowest_writes["writes"]:,} كتابة أساسية (و {lowest_total_writes.get("total_writes", lowest_total_writes["writes"]):,} شاملة المخازن لـ {NAMES[lowest_total_writes["algorithm"]]})',
        ),
        _card(
            "أقل وسيط زمن مرصود",
            NAMES[fastest["algorithm"]],
            f'{fastest["median_ns"] / 1e6:.3f} ms · هذه التجربة فقط',
        ),
        "</div>",
        '<div class="aba-warning"><b>كيف تقرأ الأرقام؟</b> '
        "كل عمود يقارن خوارزميات على نفس القائمة. طول العمود يمثل قيمة المقياس؛ الأقصر أفضل. "
        "المقارنات ≠ الكتابات ≠ الزمن، ولا تجمعها في درجة واحدة. "
        + escape(caveat)
        + "</div>",
        '<div class="aba-chart-grid">',
        _bars(rows, "comparisons", "01 · المقارنات بين القيم", "", 0),
        _bars(rows, "writes", "02 · الكتابات في القائمة", "", 0),
        _bars(
            [{**r, "median_ms": r["median_ns"] / 1e6} for r in rows],
            "median_ms",
            "03 · وسيط زمن التنفيذ",
            "ms",
            3,
        ),
        "</div>",
        '<section class="aba-panel"><h3>التفاصيل الدقيقة (شاملة حركة المخازن المؤقتة والذاكرة الإضافية)</h3>'
        '<div class="aba-table-wrap"><table class="aba-table"><thead><tr>'
        "<th>الخوارزمية</th><th>المقارنات</th><th>التبديلات</th><th>الكتابات الأساسية</th>"
        "<th>كتابة المخازن (Aux)</th><th>إجمالي الكتابات</th><th>أقصى ذاكرة إضافية</th>"
        "<th>الاستقرار</th><th>وسيط الوقت (ms)</th><th>المدى (ms)</th></tr></thead><tbody>",
    ]
    for row in rows:
        alg = row["algorithm"]
        meta = ALGORITHM_META[alg]
        aux_w = row.get("aux_writes", 0)
        tot_w = row.get("total_writes", row["writes"] + aux_w)
        max_sp = row.get("max_aux_space", 0)
        stable_txt = "مستقر ✓" if meta["stable"] else "غير مستقر ✗"
        parts.append(
            "<tr>"
            + f"<th>{escape(NAMES[alg])}</th>"
            + "".join(
                f'<td dir="ltr">{row[key]:,}</td>'
                for key in ("comparisons", "swaps", "writes")
            )
            + f'<td dir="ltr">{aux_w:,}</td>'
            + f'<td dir="ltr">{tot_w:,}</td>'
            + f'<td dir="ltr">{max_sp:,} ({escape(meta["space"])})</td>'
            + f"<td>{stable_txt}</td>"
            + f'<td dir="ltr">{row["median_ns"] / 1e6:.4f}</td>'
            + f'<td dir="ltr">{row["min_ns"] / 1e6:.4f} – {row["max_ns"] / 1e6:.4f}</td></tr>'
        )
    parts.append("</tbody></table></div></section>")
    quick_row = next((r for r in rows if r["algorithm"] == "quick"), None)
    if quick_row and (
        "تصاعديًا" in report.get("origin", "")
        or "تنازليًا" in report.get("origin", "")
        or "متساوية" in report.get("origin", "")
    ):
        insight = (
            f"Quick Sort (بمحور أخير) أجرى هنا {quick_row['comparisons']:,} مقارنة لأن ترتيب البيانات أو تساويها "
            "يدفع التقسيم إلى جانب واحد O(n²). قارنه في الجدول مع Quick Sort (3-Way Median-3) لترى كيف يحل المحور الثلاثي والتقسيم الثلاثي هذه المشكلة جذريًا!"
        )
    else:
        insight = (
            "Merge يقسّم ثم يدمج، Quick يقسم حول محور، وHeap يبني كومة. "
            "قارن الأعداد المرصودة ثم جرّب نمطًا آخر ولاحظ تغيرها."
        )
    parts.append(
        '<section class="aba-insight"><h3>لماذا ظهرت هذه النتيجة؟</h3>'
        f"<p>{escape(insight)}</p>"
        "<p>يعرض الجدول الآن كلًا من <b>الكتابات الأساسية</b> في المصفوفة و<b>كتابة المخازن المؤقتة (Aux Writes)</b> الخاصة بـ Merge Sort حتى تكون المقارنة عادلة تمامًا.</p></section>"
        '<section class="aba-panel"><h3>التعقيد المتوقع</h3>'
        "<p><b>Merge:</b> ‏O(n log n) في كل الحالات، مساحة إضافية O(n). "
        "<b>Quick (Last Pivot):</b> متوسط O(n log n) وأسوأ حالة O(n²) عند محور الطرف الأخير. "
        "<b>Quick (3-Way Median-3):</b> يعالج البيانات المرتبة في O(n log n) والمتساوية في O(n). "
        "<b>Heap:</b> أسوأ حالة O(n log n) ومساحة إضافية O(1). "
        "<b>Insertion:</b> ‏O(n) للمرتب وشبه المرتب وO(n²) للعشوائي.</p></section></div>"
    )
    return "".join(parts)


def compare_scaling(pattern="عشوائي", seed=42, base_size=60, steps=4, repeats=5, algorithms=None):
    """Run multi-size asymptotic scaling experiment across n, 2n, 4n, 8n..."""
    selected = list(
        ("merge", "quick", "quick3", "heap", "insertion")
        if algorithms is None
        else algorithms
    )
    sizes = [int(base_size) * (2**i) for i in range(int(steps))]
    sizes = [min(1200, max(10, s)) for s in sizes]
    series = {name: [] for name in selected}
    for n in sizes:
        data = dataset(n, pattern, int(seed))
        rep = benchmark(data, repeats=repeats, algorithms=selected)
        for row in rep["results"]:
            series[row["algorithm"]].append(row)
    return dict(pattern=pattern, seed=seed, sizes=sizes, series=series)


def render_scaling_report(scaling):
    sizes = scaling["sizes"]
    series = scaling["series"]
    pattern = scaling["pattern"]
    # Build SVG curve for comparisons
    width, height = 680, 260
    pad_l, pad_r, pad_t, pad_b = 65, 25, 25, 40
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b
    max_comp = max(
        (pt["comparisons"] for pts in series.values() for pt in pts), default=1
    ) or 1

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="260">',
        f'<line x1="{pad_l}" y1="{pad_t+plot_h}" x2="{width-pad_r}" y2="{pad_t+plot_h}" stroke="#64748b" stroke-width="1.5"/>',
        f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{pad_t+plot_h}" stroke="#64748b" stroke-width="1.5"/>',
        f'<text x="{pad_l-8}" y="{pad_t+10}" text-anchor="end" fill="#94a3b8" font-size="11">{max_comp:,}</text>',
        f'<text x="{pad_l-8}" y="{pad_t+plot_h}" text-anchor="end" fill="#94a3b8" font-size="11">0</text>',
    ]
    for idx, n in enumerate(sizes):
        x = pad_l + (idx / max(1, len(sizes) - 1)) * plot_w
        svg.append(
            f'<text x="{x:.1f}" y="{height-12}" text-anchor="middle" fill="#cbd5e1" font-size="12">n={n}</text>'
        )
    for alg, pts in series.items():
        color = COLORS.get(alg, "#38bdf8")
        coords = []
        for idx, pt in enumerate(pts):
            x = pad_l + (idx / max(1, len(sizes) - 1)) * plot_w
            y = pad_t + plot_h - (pt["comparisons"] / max_comp) * plot_h
            coords.append((x, y, pt["comparisons"]))
        poly = " ".join(f"{x:.1f},{y:.1f}" for x, y, _ in coords)
        svg.append(f'<polyline fill="none" stroke="{color}" stroke-width="3" points="{poly}"/>')
        for x, y, c in coords:
            svg.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{color}"><title>{NAMES[alg]}: {c:,}</title></circle>'
            )
    svg.append("</svg>")

    legend = "".join(
        f'<span><i style="background:{COLORS.get(alg, "#38bdf8")}"></i>{escape(NAMES[alg])}</span>'
        for alg in series
    )

    parts = [
        f'<div class="aba-report" dir="rtl"><header class="aba-report-head">'
        f'<span class="aba-kicker">مختبر النمو التقاربي ورتب Big-O · Asymptotic Scaling Lab</span>'
        f'<h2>منحنى النمو ونسبة التضاعف التجريبية (Doubling Ratio)</h2>'
        f'<p>النمط: {escape(pattern)} | الأحجام المختبرة: {", ".join(map(str, sizes))}</p></header>',
        '<div class="aba-warning"><b>القاعدة الأكاديمية لنسبة التضاعف C(2n)/C(n):</b> '
        'عند مضاعفة حجم المدخلات (2n)، إذا كانت النسبة <b>≈ 2.0</b> فالسلوك خطي Θ(n)؛ '
        'وإذا كانت <b>≈ 2.1 – 2.3</b> فالسلوك Θ(n log n)؛ '
        'وإذا قفزت إلى <b>≈ 4.0</b> فالسلوك تربيعي Θ(n²)!</div>',
        '<section class="aba-panel"><h3>منحنى نمو عدد المقارنات مع تضاعف حجم البيانات (n)</h3>'
        f'<div class="aba-legend">{legend}</div>'
        f'<div class="aba-chart" dir="ltr">{"".join(svg)}</div></section>',
        '<section class="aba-panel"><h3>جدول القياس التقاربي ونسبة التضاعف C(2n)/C(n)</h3>'
        '<div class="aba-table-wrap"><table class="aba-table"><thead><tr><th>الخوارزمية</th>',
    ]
    for n in sizes:
        parts.append(f'<th dir="ltr">n={n} (مقارنة / زمن)</th>')
    parts.append("<th>متوسط نسبة التضاعف C(2n)/C(n)</th><th>الاستنتاج التجريبي</th></tr></thead><tbody>")

    for alg, pts in series.items():
        ratios = []
        for i in range(1, len(pts)):
            prev_c = max(1, pts[i - 1]["comparisons"])
            ratios.append(pts[i]["comparisons"] / prev_c)
        avg_ratio = sum(ratios) / len(ratios) if ratios else 0.0
        if avg_ratio >= 3.4:
            inferred = "تربيعي Θ(n²) ⚠️"
        elif avg_ratio >= 2.05:
            inferred = "شبه خطي لوغاريتمي Θ(n log n) ✅"
        elif avg_ratio >= 1.7:
            inferred = "خطي Θ(n) 🚀"
        else:
            inferred = "ثابت/تحت خطي"
        parts.append(f"<tr><th>{escape(NAMES[alg])}</th>")
        for pt in pts:
            parts.append(
                f'<td dir="ltr">{pt["comparisons"]:,} ({pt["median_ns"]/1e6:.2f} ms)</td>'
            )
        parts.append(
            f'<td dir="ltr"><b>{avg_ratio:.2f}x</b></td><td>{inferred}</td></tr>'
        )
    parts.append("</tbody></table></div></section></div>")
    return "".join(parts)
