"""Pure rendering helpers used by the Colab/Gradio interface."""
from html import escape

from .sorting import ALGORITHM_META, build_initial_tags, run_sort


AR_NAMES = {k: v["name"] for k, v in ALGORITHM_META.items()}
EVENT_AR = {
    "start": "بدء الترتيب",
    "done": "اكتمل الترتيب",
    "compare": "مقارنة عنصرين",
    "swap": "تبديل عنصرين",
    "write": "كتابة قيمة في المصفوفة",
    "divide": "تقسيم المجال",
    "merge": "دمج جزأين مرتبين",
    "pivot": "اختيار المحور",
    "partition": "اكتمال التقسيم حول المحور",
    "heapify": "إصلاح خاصية الكومة",
    "extract": "نقل عنصر إلى موضعه النهائي",
}


def parse_values(text):
    text = (text or "").strip()
    if not text:
        raise ValueError("أدخل أعدادًا مفصولة بفواصل، مثل: 8,3,5,1")
    try:
        values = [int(part.strip()) for part in text.split(",")]
    except ValueError as exc:
        raise ValueError("المدخلات يجب أن تكون أعدادًا صحيحة مفصولة بفواصل") from exc
    if len(values) > 80:
        raise ValueError("للمحاكاة المرئية استخدم 80 عنصرًا أو أقل")
    return values


def resolve_algorithm_key(algorithm):
    raw = str(algorithm).strip().lower()
    if "3-way" in raw or "quick3" in raw or "ثلاثي" in raw:
        return "quick3"
    if "insertion" in raw or "إدراج" in raw:
        return "insertion"
    if "selection" in raw or "اختيار" in raw:
        return "selection"
    first = raw.split()[0] if raw else ""
    aliases = {
        "merge": "merge",
        "quick": "quick",
        "quick3": "quick3",
        "heap": "heap",
        "insertion": "insertion",
        "selection": "selection",
    }
    if first not in aliases:
        raise ValueError("اختر خوارزمية صحيحة")
    return aliases[first]


def build_session(text, algorithm, event_limit=20000):
    values = parse_values(text)
    key = resolve_algorithm_key(algorithm)
    return run_sort(values, key, trace=True, event_limit=event_limit)


def replay_until(result, step_index):
    state = result["input"][:]
    events = result["events"]
    if not events:
        return state, None
    index = max(0, min(int(step_index), len(events) - 1))
    for event in events[: index + 1]:
        if event["kind"] == "swap":
            i, j = event["indices"]
            state[i], state[j] = state[j], state[i]
        elif event["kind"] == "write":
            state[event["index"]] = event["value"]
    return state, events[index]


def replay_with_tags(result, step_index):
    """Replay both integer state, duplicate stability tags, and active merge buffers."""
    state = result["input"][:]
    tags = result.get("initial_tags", build_initial_tags(state))[:]
    events = result["events"]
    if not events:
        return state, tags, None, None
    index = max(0, min(int(step_index), len(events) - 1))
    active_merge = None
    merge_tag_snapshot = {}
    for event in events[: index + 1]:
        kind = event["kind"]
        if kind == "merge":
            lo, mid, hi = event["lo"], event["mid"], event["hi"]
            active_merge = dict(lo=lo, mid=mid, hi=hi, left=event["left"], right=event["right"])
            merge_tag_snapshot = {idx: tags[idx] for idx in range(lo, hi)}
        elif kind == "swap":
            i, j = event["indices"]
            state[i], state[j] = state[j], state[i]
            tags[i], tags[j] = tags[j], tags[i]
        elif kind == "write":
            k = event["index"]
            state[k] = event["value"]
            src = event.get("source_tag")
            if src is not None and src in merge_tag_snapshot:
                tags[k] = merge_tag_snapshot[src]
    return state, tags, events[index], active_merge


def event_explanation(event):
    if not event:
        return "لا توجد خطوة"
    kind = event["kind"]
    title = EVENT_AR.get(kind, kind)
    if kind == "compare":
        x, y = event["values"]
        decision = "نعم — تحقق الشرط" if event["result"] else "لا — لم يتحقق الشرط"
        buffer_note = " (من مخزني الدمج المؤقتين)" if event.get("source") == "merge_buffers" else ""
        return f"{title}: هل {x} {event['operator']} {y}؟ {decision}{buffer_note}"
    if kind == "swap":
        return f"{title} في الموضعين {event['indices'][0]} و{event['indices'][1]}"
    if kind == "write":
        return f"{title}: وضع {event['value']} في الموضع {event['index']}"
    if kind == "pivot":
        return f"{title}: القيمة {event['value']} في الموضع {event['index']}"
    if kind in {"divide", "merge", "partition"}:
        text = f"{title}: من الفهرس {event['lo']} إلى {event['hi'] - 1}"
        if kind == "merge":
            text += f"؛ اليسار {event['left']} واليمين {event['right']}"
        return text
    if kind == "heapify":
        return f"{title}: الجذر {event['root']}، حجم الكومة {event['heap_size']}"
    if kind == "extract":
        return f"{title}: الموضع النهائي {event['sorted_index']}"
    return title


def render_step(result, step_index):
    state, tags, event, active_merge = replay_with_tags(result, step_index)
    highlighted = set()
    pivot = set()
    written = set()
    muted = set()
    if event:
        if event["kind"] in {"compare", "swap"}:
            highlighted.update(event.get("indices", []))
            if result["algorithm"] in {"quick", "quick3"} and event["kind"] == "compare":
                pivot.add(event["indices"][1])
        elif event["kind"] == "write":
            written.add(event["index"])
        elif event["kind"] == "pivot":
            pivot.add(event["index"])
        elif event["kind"] == "heapify":
            pivot.add(event["root"])
        elif event["kind"] == "extract":
            written.add(event["sorted_index"])
        if "lo" in event and "hi" in event:
            muted = set(range(len(state))) - set(range(event["lo"], event["hi"]))
    scale = max((abs(v) for v in state), default=1) or 1
    width = max(560, 80 + 48 * len(state))
    zero_y, amplitude = 143, 99
    bars = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 300" '
        f'width="{width}" height="300" role="img" aria-label="المصفوفة بفهرس تصاعدي من اليسار لليمين وخط الصفر في الوسط">',
        f'<line x1="40" y1="{zero_y}" x2="{width-8}" y2="{zero_y}" stroke="#94a3b8" stroke-width="2"/>',
        f'<text x="5" y="{zero_y - amplitude}" fill="#94a3b8" font-size="13">+{scale}</text>',
        f'<text x="13" y="{zero_y - 5}" fill="#e2e8f0" font-size="13">0</text>',
        f'<text x="5" y="{zero_y + amplitude + 18}" fill="#94a3b8" font-size="13">−{scale}</text>',
    ]
    for i, value in enumerate(state):
        height = max(3, round(amplitude * abs(value) / scale))
        top = zero_y - height if value >= 0 else zero_y
        x = 47 + 48 * i
        color = "#38bdf8"
        if i in highlighted:
            color = "#f97316"
        if i in written:
            color = "#a78bfa"
        if i in pivot:
            color = "#f43f5e"
        opacity = "0.36" if i in muted else "1"
        label_y = max(16, top - 7) if value >= 0 else min(265, zero_y + height + 16)
        tag_label = tags[i] if len(state) <= 24 else str(value)
        bars.append(
            f'<g opacity="{opacity}"><title>الفهرس {i}: {tag_label}</title>'
            f'<rect x="{x}" y="{top}" width="30" height="{height}" rx="4" fill="{color}"/>'
            f'<text x="{x+15}" y="{label_y}" text-anchor="middle" fill="#f8fafc" font-size="12">{escape(tag_label)}</text>'
            f'<text x="{x+15}" y="288" text-anchor="middle" fill="#94a3b8" font-size="12">{i}</text></g>'
        )
    bars.append("</svg>")
    index = 0 if not result["events"] else max(0, min(int(step_index), len(result["events"]) - 1))
    previous_events = result["events"][: index + 1]
    comparisons = sum(e["kind"] == "compare" for e in previous_events)
    swaps = sum(e["kind"] == "swap" for e in previous_events)
    writes = swaps * 2 + sum(e["kind"] == "write" for e in previous_events)
    metrics = result["metrics"]
    explanatory = {
        "merge": "قسّم ← رتّب النصفين ← ادمج. عند التعادل يختار العنصر الأيسر فيحافظ على الاستقرار (لاحظ علامات أ، ب).",
        "quick": "اختَر آخر عنصر محورًا (Lomuto)، ثم انقل الأصغر أو المساوي إلى يساره.",
        "quick3": "اختَر وسيط 3 عناصر محورًا، ثم قسّم إلى 3 مناطق (< محور، == محور، > محور) لتفادي فخ O(n²).",
        "heap": "ابنِ Max Heap؛ الجذر هو الأكبر، ويُنقل تباعًا إلى نهاية القائمة بذاكرة إضافية O(1).",
        "insertion": "أدرج كل عنصر في موضعه الصحيح ضمن الجزء الأيسر المرتب؛ مستقر وسريع جدًا للمصفوفات شبه المرتبة.",
        "selection": "ابحث عن أصغر عنصر في الجزء غير المرتب وبدّله مرة واحدة فقط في كل جولة.",
    }[result["algorithm"]]

    buffer_box = ""
    if result["algorithm"] == "merge" and active_merge and event and event["kind"] in {"merge", "compare", "write"}:
        buffer_box = (
            f'<div class="aba-event" style="border-inline-start-color:#38bdf8;margin-top:8px">'
            f'<b>مخزنا الدمج المؤقتان للمجال [{active_merge["lo"]}..{active_merge["hi"]-1}]:</b> '
            f'<span dir="ltr">Left = {active_merge["left"]} | Right = {active_merge["right"]}</span></div>'
        )

    truncated = (
        '<p class="aba-truncated">السجل بلغ الحد؛ الخطوات المتبقية غير محفوظة، '
        "لكن الناتج والعدادات الكلية صحيحة.</p>"
        if metrics["trace_truncated"]
        else ""
    )
    return f"""<div dir="rtl" class="aba-card">
      <div class="aba-sim-top"><span class="aba-kicker">محاكاة خطوة بخطوة · تتبع الاستقرار (أ، ب)</span>
      <span class="aba-count">الخطوة {index + 1} / {len(result['events'])}</span></div>
      <h2>{escape(AR_NAMES[result['algorithm']])}</h2>
      <p class="aba-method">{escape(explanatory)}</p>
      <div class="aba-event"><b>{escape(EVENT_AR.get(event['kind'], 'حدث') if event else '')}</b>
      <span>{escape(event_explanation(event))}</span></div>
      {buffer_box}
      <div class="aba-chart" dir="ltr">{''.join(bars)}</div>
      <div class="aba-legend"><span><i style="background:#38bdf8"></i>عنصر</span>
      <span><i style="background:#f97316"></i>مقارنة/تبديل</span>
      <span><i style="background:#a78bfa"></i>كتابة/استخراج</span>
      <span><i style="background:#f43f5e"></i>محور/جذر</span></div>
      <div class="aba-progress"><span>حتى هذه اللحظة: {comparisons:,} مقارنة · {swaps:,} تبديل · {writes:,} كتابة</span>
      <span>الإجمالي: {metrics['comparisons']:,} مقارنة · {metrics['swaps']:,} تبديل · {metrics['writes']:,} كتابة أساسية</span></div>
      <small class="aba-index-note">الفهرس 0 يبدأ من اليسار. فوق الخط = موجب، تحته = سالب. الرموز (أ، ب) تميّز العناصر المتكررة لاختبار الاستقرار.</small>
      {truncated}</div>"""


def metrics_rows(result):
    metrics = result["metrics"]
    return [
        [
            AR_NAMES[result["algorithm"]],
            len(result["input"]),
            metrics["comparisons"],
            metrics["swaps"],
            metrics["writes"],
            metrics["recorded_events"],
        ]
    ]


CSS = """
.gradio-container{direction:rtl!important;max-width:1320px!important;background:#f5f7fb!important}
.aba-hero{background:linear-gradient(125deg,#0f172a,#1e3a8a);color:white;border-radius:22px;padding:26px 30px;margin-bottom:16px}
.aba-hero small{letter-spacing:.08em;color:#67e8f9}.aba-hero h1{color:white!important;margin:8px 0 3px}.aba-hero p{color:#cbd5e1}
.aba-section{background:white;border:1px solid #e2e8f0;border-radius:18px;padding:18px;margin:12px 0}
.aba-card,.aba-report{background:#111827;color:#e2e8f0;border-radius:18px;padding:22px;border:1px solid #26364e;line-height:1.65}
.aba-card h2,.aba-report h2{color:#f8fafc;margin:4px 0}.aba-card p,.aba-report p{margin:8px 0}
.aba-sim-top,.aba-progress{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
.aba-kicker{color:#67e8f9;font-weight:700;font-size:13px}.aba-count{background:#1e293b;padding:3px 10px;border-radius:99px}
.aba-method{color:#cbd5e1}.aba-event{border-inline-start:4px solid #fb923c;background:#1d2a3d;border-radius:10px;padding:12px 16px;margin:16px 0;display:flex;gap:14px;flex-wrap:wrap}
.aba-event b{color:#fdba74}.aba-chart{overflow-x:auto;background:#0b1220;border:1px solid #334155;border-radius:14px;padding:8px;margin-top:12px}
.aba-legend{display:flex;gap:16px;flex-wrap:wrap;margin:14px 0;font-size:13px}.aba-legend span{display:flex;align-items:center;gap:5px}.aba-legend i{width:11px;height:11px;border-radius:3px}
.aba-progress{background:#1d2a3d;padding:12px;border-radius:10px;color:#e2e8f0}.aba-index-note{color:#94a3b8}.aba-truncated{color:#fdba74}
.aba-report-head p{color:#cbd5e1}.aba-report h3{color:#f8fafc;font-size:17px;margin:0 0 10px}
.aba-stat-grid,.aba-chart-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:16px 0}
.aba-stat,.aba-panel,.aba-insight,.aba-warning{border:1px solid #334155;border-radius:14px;padding:16px;background:#1d2a3d}
.aba-stat{display:flex;flex-direction:column;gap:6px}.aba-stat small,.aba-hint{color:#a5b4c8}.aba-stat strong{color:#f8fafc;font-size:21px}.aba-stat span{color:#67e8f9;font-size:13px}
.aba-warning{border-color:#a16207;background:#3a2a19;color:#fde68a}.aba-panel{min-width:0}.aba-hint{font-size:12px}
.aba-metric-row{display:grid;grid-template-columns:145px minmax(40px,1fr) 105px;gap:8px;align-items:center;margin:15px 0;font-size:13px}
.aba-metric-row b{text-align:left;white-space:nowrap}.aba-track{background:#334155;height:14px;border-radius:10px;overflow:hidden;direction:ltr}.aba-track>div{height:100%;border-radius:10px}
.aba-table-wrap{overflow-x:auto}.aba-table{width:100%;border-collapse:collapse;min-width:680px}.aba-table th,.aba-table td{padding:9px;border-bottom:1px solid #334155;text-align:right}.aba-table td{text-align:left}.aba-insight{border-color:#155e75;background:#102e3a}
@media(max-width:760px){.aba-hero{padding:18px}.aba-stat-grid,.aba-chart-grid{grid-template-columns:1fr}.aba-card,.aba-report{padding:14px}.aba-metric-row{grid-template-columns:110px minmax(30px,1fr) 90px}.aba-stat strong{font-size:18px}}
"""
