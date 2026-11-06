"""Arabic/English Gradio Dashboard for Algorithm Battle Arena v1.0.0."""
import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import random

import gradio as gr

from arena.advisor import QUIZ_QUESTIONS, advise_algorithm, grade_quiz, render_advice_html
from arena.analysis import (
    PATTERNS,
    compare,
    compare_scaling,
    dataset,
    render_report,
    render_scaling_report,
)
from arena.benchmark import benchmark
from arena.graphs import compare_pathfinding, render_pathfinding_battle
from arena.searching import (
    SEARCH_META,
    benchmark_search,
    render_search_report,
    render_search_step,
    run_search,
)
from arena.sorting import ALGORITHM_META
from arena.ui_helpers import CSS, build_session, parse_values, render_step


DEFAULT_VALUES = "8,3,5,1,3,-2"
DEFAULT_SESSION = build_session(DEFAULT_VALUES, "Merge Sort")
SORT_CHOICES = [v["name"] for v in ALGORITHM_META.values()]
NAME_TO_KEY = {v["name"]: k for k, v in ALGORITHM_META.items()}

DEFAULT_SEARCH_VALUES = "-12,-5,-2,1,3,5,8,14,21,34,55,89"
DEFAULT_SEARCH_SESSION = run_search(
    [int(x) for x in DEFAULT_SEARCH_VALUES.split(",")], 21, "binary"
)


def make_preview(size, seed, pattern):
    """Small arrays are for replay; large arrays belong in comparison."""
    n = int(size)
    rng = random.Random(int(seed))
    values = [rng.randint(-99, 99) for _ in range(n)]
    if pattern == "مرتب تصاعديًا":
        values.sort()
    elif pattern == "مرتب تنازليًا":
        values.sort(reverse=True)
    elif pattern == "قيم متساوية":
        values = [7] * n
    elif pattern == "شبه مرتب":
        values.sort()
        for _ in range(max(1, n // 6)):
            if n >= 2:
                i = rng.randrange(n - 1)
                values[i], values[i + 1] = values[i + 1], values[i]
    return ",".join(map(str, values))


def start(values, algorithm):
    try:
        session = build_session(values, algorithm)
        last = max(0, len(session["events"]) - 1)
        status = "الخطوة الأولى جاهزة. اضغط ▶ تشغيل أو استخدم التالي/السابق."
        return (
            session,
            gr.Slider(minimum=0, maximum=last, value=0, step=1),
            render_step(session, 0),
            status,
            gr.Timer(active=False),
        )
    except Exception as exc:
        return (
            None,
            gr.Slider(minimum=0, maximum=1, value=0, step=1),
            "",
            f"⚠️ {exc}",
            gr.Timer(active=False),
        )


def show_step(session, step):
    return render_step(session, step) if session else ""


def move(session, step, delta):
    if not session:
        return 0
    return max(0, min(int(step) + delta, len(session["events"]) - 1))


def play(session, step, speed):
    if not session:
        return gr.Timer(active=False), step, "أنشئ المحاكاة أولًا."
    last = len(session["events"]) - 1
    index = 0 if int(step) >= last else int(step)
    return gr.Timer(value=float(speed), active=True), index, "المحاكاة تعمل الآن…"


def advance(session, step, speed):
    if not session:
        return step, gr.Timer(active=False), "أنشئ المحاكاة أولًا."
    last = len(session["events"]) - 1
    next_step = min(int(step) + 1, last)
    if next_step >= last:
        return next_step, gr.Timer(active=False), "اكتمل ترتيب المصفوفة."
    return next_step, gr.skip(), "المحاكاة تعمل الآن…"


def parse_manual(text):
    parts = (text or "").split(",")
    try:
        values = [int(part.strip()) for part in parts]
    except ValueError as exc:
        raise ValueError("اكتب أعدادًا صحيحة مفصولة بفاصلة، مثل 8,3,5,1") from exc
    if not 1 <= len(values) <= 1200:
        raise ValueError("التجربة تحتاج من 1 إلى 1200 عنصر")
    return values


def compare_all(source, values, size, pattern, seed, selected_names):
    try:
        keys = [NAME_TO_KEY[n] for n in (selected_names or []) if n in NAME_TO_KEY]
        if not keys:
            keys = ["merge", "quick", "quick3", "heap"]
        manual = parse_manual(values) if source == "المصفوفة المدخلة" else []
        report = compare(
            manual, source, int(size), pattern, int(seed), repeats=9, algorithms=keys
        )
        return report, render_report(report), "✅ تم التحقق من تطابق نتائج جميع الخوارزميات المختارة."
    except Exception as exc:
        return None, "", f"⚠️ {exc}"


def save_report(report):
    if not report:
        return "شغّل المقارنة أولًا ثم احفظ التقرير."
    output_dir = Path(os.environ.get("ARENA_RESULTS_DIR", "outputs/reports"))
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    stem = f"sorting_comparison_{stamp}"
    with (output_dir / f"{stem}.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
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
    with (output_dir / f"{stem}.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(report["results"])
    return f"💾 حُفظ ملفا CSV وJSON داخل: {output_dir}"


def run_scaling_ui(pattern, seed, base_size, steps, selected_names):
    try:
        keys = [NAME_TO_KEY[n] for n in (selected_names or []) if n in NAME_TO_KEY]
        if not keys:
            keys = ["merge", "quick", "quick3", "heap"]
        scaling = compare_scaling(
            pattern=pattern,
            seed=int(seed),
            base_size=int(base_size),
            steps=int(steps),
            repeats=5,
            algorithms=keys,
        )
        return render_scaling_report(scaling)
    except Exception as exc:
        return f"<div class='aba-warning'>⚠️ {exc}</div>"


def run_search_ui(values_txt, target_val, alg_label):
    try:
        vals = parse_values(values_txt)
        key_map = {v["name"]: k for k, v in SEARCH_META.items()}
        key = key_map.get(alg_label, "binary")
        sess = run_search(vals, int(target_val), key)
        last = max(0, len(sess["events"]) - 1)
        bench = benchmark_search(vals, int(target_val), repeats=7)
        return (
            sess,
            gr.Slider(minimum=0, maximum=last, value=last, step=1),
            render_search_step(sess, last),
            render_search_report(bench),
        )
    except Exception as exc:
        return (
            None,
            gr.Slider(minimum=0, maximum=1, value=0, step=1),
            f"<div class='aba-warning'>⚠️ {exc}</div>",
            "",
        )


def show_search_step_ui(sess, idx):
    return render_search_step(sess, idx) if sess else ""


def run_graph_ui(preset, seed):
    battle = compare_pathfinding(preset=preset, seed=int(seed))
    return render_pathfinding_battle(battle)


def run_advisor_ui(source, manual_txt, size, pattern, seed, need_stable, strict_mem):
    try:
        data = (
            parse_manual(manual_txt)
            if source == "المصفوفة المدخلة"
            else dataset(int(size), pattern, int(seed))
        )
        advice = advise_algorithm(
            data, need_stable=bool(need_stable), strict_memory=bool(strict_mem)
        )
        bench = benchmark(data, repeats=5, algorithms=list(ALGORITHM_META))
        return render_advice_html(advice, bench)
    except Exception as exc:
        return f"<div class='aba-warning'>⚠️ {exc}</div>"


with gr.Blocks(css=CSS, title="Algorithm Battle Arena v1.0 | Interactive CS Lab") as demo:
    gr.HTML(
        """<div class="aba-hero" dir="rtl">
      <small>ANALYSIS & DESIGN OF ALGORITHMS · INTERACTIVE BENCHMARK & VISUALIZATION SUITE v1.0</small>
      <h1>⚔️ Algorithm Battle Arena — ساحة معارك الخوارزميات</h1>
      <p>مختبر تفاعلي متكامل لمحاكاة ومقارنة خوارزميات الترتيب والبحث والمسارات الشبكية ورتب النمو التقاربي (Big-O) عمليًا.</p>
      <small>إعداد: عبدالوهاب يحيى محمد عامر · إشراف نظري: د. معاذ الصبري · إشراف عملي: م. محمد الوصابي</small>
    </div>"""
    )

    with gr.Tab("01 · محاكاة الترتيب (Sorting Visualizer)"):
        gr.Markdown("### شاهد كيف تعمل 6 خوارزميات ترتيب خطوة بخطوة مع تتبع الاستقرار والمخازن المؤقتة")
        with gr.Row():
            values = gr.Textbox(
                value=DEFAULT_VALUES,
                label="المصفوفة: أعداد صحيحة مفصولة بفواصل (حتى 80 عنصرًا)",
                placeholder="8,3,5,1,3,-2",
                scale=3,
                rtl=False,
            )
            algorithm = gr.Dropdown(
                SORT_CHOICES, value="Merge Sort", label="الخوارزمية", scale=2
            )
        with gr.Row():
            size = gr.Slider(3, 36, value=12, step=1, label="عدد عناصر المحاكاة")
            pattern = gr.Dropdown(list(PATTERNS), value="عشوائي", label="نمط التوليد")
            seed = gr.Number(value=42, precision=0, label="البذرة")
            generate = gr.Button("🎲 توليد")
            run = gr.Button("▶ ابدأ المحاكاة", variant="primary")
        status = gr.Markdown("البيانات الافتراضية جاهزة. عدّلها أو ابدأ المحاكاة.")
        visual = gr.HTML(value=render_step(DEFAULT_SESSION, 0))
        session = gr.State(DEFAULT_SESSION)
        step = gr.Slider(
            0, len(DEFAULT_SESSION["events"]) - 1, value=0, step=1, label="الانتقال إلى حدث"
        )
        with gr.Row():
            previous = gr.Button("السابق")
            play_button = gr.Button("▶ تشغيل تلقائي", variant="primary")
            pause_button = gr.Button("⏸ إيقاف")
            next_button = gr.Button("التالي")
        speed = gr.Slider(
            0.15,
            1.5,
            value=0.6,
            step=0.05,
            label="فاصل الزمن بين الأحداث (ثانية)؛ غيّره ثم اضغط تشغيل",
        )
        timer = gr.Timer(value=0.6, active=False)

    with gr.Tab("02 · مقارنة الترتيب (Benchmark Arena)"):
        gr.Markdown("### تجربة معيارية عادلة: نفس المدخلات، قياس زمني معزول بـ 9 تكرارات، وحساب لحركة المخازن المؤقتة")
        with gr.Row():
            source = gr.Radio(
                ["بيانات مولدة", "المصفوفة المدخلة"],
                value="بيانات مولدة",
                label="مصدر بيانات المقارنة",
            )
            bench_size = gr.Slider(
                10, 1200, value=300, step=10, label="حجم البيانات المولدة"
            )
        with gr.Row():
            bench_pattern = gr.Dropdown(
                list(PATTERNS), value="عشوائي", label="نمط البيانات"
            )
            bench_seed = gr.Number(
                value=42, precision=0, label="البذرة (تعيد التجربة نفسها)"
            )
        bench_algs = gr.CheckboxGroup(
            SORT_CHOICES,
            value=SORT_CHOICES[:5],
            label="الخوارزميات المشاركة في المعركة",
        )
        compare_button = gr.Button("📊 شغّل المقارنة والتحليل", variant="primary")
        compare_status = gr.Markdown()
        report_state = gr.State()
        report_view = gr.HTML()
        save_button = gr.Button("💾 احفظ نتائج التجربة CSV + JSON")
        save_status = gr.Markdown()

    with gr.Tab("03 · مختبر النمو التقاربي (Big-O Scaling Lab)"):
        gr.Markdown("### إثبات رتب النمو (Θ(n), Θ(n log n), Θ(n²)) عمليًا عبر مضاعفة حجم المدخلات وحساب نسبة التضاعف")
        with gr.Row():
            scale_pattern = gr.Dropdown(
                list(PATTERNS), value="عشوائي", label="نمط البيانات"
            )
            scale_seed = gr.Number(value=42, precision=0, label="البذرة")
            scale_base = gr.Slider(
                30, 150, value=60, step=10, label="الحجم الابتدائي (n)"
            )
            scale_steps = gr.Slider(
                3, 5, value=4, step=1, label="عدد المضاعفات (n, 2n, 4n...)"
            )
        scale_algs = gr.CheckboxGroup(
            SORT_CHOICES,
            value=[
                "Merge Sort",
                "Quick Sort (Last Pivot)",
                "Quick Sort (3-Way Median-3)",
                "Heap Sort",
                "Insertion Sort",
            ],
            label="الخوارزميات",
        )
        scale_btn = gr.Button("📈 ارسم منحنى النمو واحسب نسبة التضاعف", variant="primary")
        scale_html = gr.HTML(
            value=render_scaling_report(
                compare_scaling("عشوائي", 42, 60, 4, repeats=3)
            )
        )

    with gr.Tab("04 · ساحة البحث (Searching Arena)"):
        gr.Markdown("### محاكاة ومقارنة خوارزميات البحث: Linear vs Binary vs Jump vs Interpolation")
        with gr.Row():
            s_values = gr.Textbox(
                value=DEFAULT_SEARCH_VALUES,
                label="عناصر المصفوفة (تُرتب تلقائيًا للبحث الثنائي والقفزي والاستيفائي)",
                scale=3,
                rtl=False,
            )
            s_target = gr.Number(value=21, precision=0, label="الهدف المطلوب بحثه", scale=1)
            s_alg = gr.Dropdown(
                [v["name"] for v in SEARCH_META.values()],
                value="Binary Search",
                label="خوارزمية المحاكاة",
                scale=1,
            )
        s_btn = gr.Button("🔍 شغّل محاكاة ومقارنة البحث", variant="primary")
        s_sess = gr.State(DEFAULT_SEARCH_SESSION)
        s_step = gr.Slider(
            0,
            len(DEFAULT_SEARCH_SESSION["events"]) - 1,
            value=len(DEFAULT_SEARCH_SESSION["events"]) - 1,
            step=1,
            label="خطوة البحث",
        )
        s_visual = gr.HTML(
            value=render_search_step(
                DEFAULT_SEARCH_SESSION, len(DEFAULT_SEARCH_SESSION["events"]) - 1
            )
        )
        s_report = gr.HTML(
            value=render_search_report(
                benchmark_search(
                    [int(x) for x in DEFAULT_SEARCH_VALUES.split(",")], 21, repeats=5
                )
            )
        )

    with gr.Tab("05 · ساحة المسارات الشبكية (Graph Arena)"):
        gr.Markdown("### مقارنة خوارزميات الرسوم البيانية (BFS, DFS, Dijkstra, A*) في إيجاد المسار الأقصر والأقل تكلفة")
        with gr.Row():
            g_preset = gr.Dropdown(
                [
                    "تضاريس موزونة (تكلفة متغيرة)",
                    "متاهة متوازنة",
                    "حاجز أوسط (اختبار الالتفاف)",
                    "مفتوحة بلا عوائق",
                ],
                value="تضاريس موزونة (تكلفة متغيرة)",
                label="بيئة الشبكة",
            )
            g_seed = gr.Number(value=42, precision=0, label="بذرة توليد الشبكة")
            g_btn = gr.Button("🧭 شغّل معركة المسارات", variant="primary")
        g_html = gr.HTML(
            value=render_pathfinding_battle(
                compare_pathfinding("تضاريس موزونة (تكلفة متغيرة)", 42)
            )
        )

    with gr.Tab("06 · المستشار الذكي والاختبار الذاتي (Advisor & Quiz)"):
        gr.Markdown("### مستشار اختيار الخوارزمية الذكي + بنك أسئلة تفاعلي للطالب")
        with gr.Row():
            adv_source = gr.Radio(
                ["بيانات مولدة", "المصفوفة المدخلة"],
                value="بيانات مولدة",
                label="مصدر البيانات لتشخيصها",
            )
            adv_size = gr.Slider(20, 600, value=200, step=20, label="حجم العينة")
            adv_pattern = gr.Dropdown(list(PATTERNS), value="شبه مرتب", label="نمط البيانات")
            adv_seed = gr.Number(value=42, precision=0, label="البذرة")
        with gr.Row():
            adv_stable = gr.Checkbox(
                value=False, label="أحتاج خوارزمية مستقرة (Stable Sort) تحافظ على ترتيب المتكررات"
            )
            adv_mem = gr.Checkbox(
                value=False, label="قيد ذاكرة صارم O(1) In-Place (منع المخازن الإضافية)"
            )
            adv_btn = gr.Button("🧠 حلل البيانات وقدّم التوصية الهندسية", variant="primary")
        adv_html = gr.HTML()

        gr.Markdown("### اختبر فهمك الأكاديمي (أسئلة مراجعة المناقشة والاختبارات)")
        q_inputs = [
            gr.Radio(item["options"], value=item["options"][0], label=item["q"])
            for item in QUIZ_QUESTIONS
        ]
        quiz_btn = gr.Button("✔️ صحّح إجاباتي واعرض التفسير العلمي", variant="secondary")
        quiz_html = gr.HTML()

    generate.click(make_preview, [size, seed, pattern], values)
    run.click(start, [values, algorithm], [session, step, visual, status, timer])
    step.change(show_step, [session, step], visual, show_progress="hidden")
    previous.click(
        lambda r, s: move(r, s, -1), [session, step], step, show_progress="hidden"
    )
    next_button.click(
        lambda r, s: move(r, s, 1), [session, step], step, show_progress="hidden"
    )
    play_button.click(
        play, [session, step, speed], [timer, step, status], show_progress="hidden"
    )
    pause_button.click(
        lambda: (gr.Timer(active=False), "توقفت المحاكاة؛ يمكنك التنقل يدويًا."),
        outputs=[timer, status],
        show_progress="hidden",
    )
    timer.tick(
        advance,
        [session, step, speed],
        [step, timer, status],
        queue=False,
        show_progress="hidden",
    )
    compare_button.click(
        compare_all,
        [source, values, bench_size, bench_pattern, bench_seed, bench_algs],
        [report_state, report_view, compare_status],
    )
    save_button.click(save_report, report_state, save_status)
    scale_btn.click(
        run_scaling_ui,
        [scale_pattern, scale_seed, scale_base, scale_steps, scale_algs],
        scale_html,
    )
    s_btn.click(
        run_search_ui, [s_values, s_target, s_alg], [s_sess, s_step, s_visual, s_report]
    )
    s_step.change(show_search_step_ui, [s_sess, s_step], s_visual, show_progress="hidden")
    g_btn.click(run_graph_ui, [g_preset, g_seed], g_html)
    adv_btn.click(
        run_advisor_ui,
        [adv_source, values, adv_size, adv_pattern, adv_seed, adv_stable, adv_mem],
        adv_html,
    )
    quiz_btn.click(grade_quiz, q_inputs, quiz_html)


if __name__ == "__main__":
    demo.launch(share=True, debug=True)
