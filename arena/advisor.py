"""Smart Algorithm Advisor (Dataset Profiler) and Interactive Self-Assessment Quiz."""
from html import escape

from .core import validate
from .sorting import ALGORITHM_META


def profile_dataset(values):
    """Compute structural metrics of an integer array to recommend the optimal algorithm."""
    data = validate(values)
    n = len(data)
    if n <= 1:
        return dict(
            n=n,
            inversion_ratio=0.0,
            duplicate_ratio=0.0,
            unique_count=n,
            is_sorted=True,
            is_reversed=True,
            pattern_label="تافهة (عنصر واحد أو فارغة)",
        )
    # Adjacent inversions & total inversions (exact for n <= 600, sampled otherwise)
    sample = data[:600]
    m = len(sample)
    max_pairs = m * (m - 1) // 2
    inversions = 0
    for i in range(m):
        vi = sample[i]
        for j in range(i + 1, m):
            if vi > sample[j]:
                inversions += 1
    inv_ratio = inversions / max_pairs if max_pairs else 0.0
    unique_count = len(set(data))
    dup_ratio = 1.0 - (unique_count / n)
    is_sorted = all(data[i] <= data[i + 1] for i in range(n - 1))
    is_reversed = all(data[i] >= data[i + 1] for i in range(n - 1))

    if unique_count == 1:
        label = "جميع القيم متساوية (100% تكرار)"
    elif is_sorted:
        label = "مرتبة تصاعديًا بالكامل"
    elif is_reversed:
        label = "مرتبة تنازليًا (معكوسة)"
    elif inv_ratio <= 0.08:
        label = "شبه مرتبة (انحرافات قليلة جدًا)"
    elif dup_ratio >= 0.50:
        label = "عشوائية مع كثافة تكرارات عالية"
    else:
        label = "عشوائية عامة"

    return dict(
        n=n,
        inversion_ratio=round(inv_ratio, 4),
        duplicate_ratio=round(dup_ratio, 4),
        unique_count=unique_count,
        is_sorted=is_sorted,
        is_reversed=is_reversed,
        pattern_label=label,
    )


def advise_algorithm(values, need_stable=False, strict_memory=False):
    prof = profile_dataset(values)
    n = prof["n"]
    reasons = []
    warnings = []

    if need_stable and strict_memory:
        chosen = "insertion"
        reasons.append("طلبت استقرارًا (Stability) مع ذاكرة إضافية O(1) صارمة؛ Insertion Sort يحقق الشرطين معًا.")
        if n > 200 and prof["inversion_ratio"] > 0.15:
            warnings.append("تنبيه: لأن الحجم كبير والبيانات غير مرتبة، سيكلف Insertion Sort زمنًا تربيعيًا Θ(n²). إذا سمحت بذاكرة O(n) فاختر Merge Sort.")
    elif need_stable:
        if n <= 32 or prof["inversion_ratio"] <= 0.06:
            chosen = "insertion"
            reasons.append("البيانات صغيرة أو شبه مرتبة مع اشتراط الاستقرار؛ Insertion Sort يعمل في زمن قريب من الخطي Θ(n) وبلا ذاكرة إضافية.")
        else:
            chosen = "merge"
            reasons.append("Merge Sort يضمن الاستقرار التام مع أداء مضمون Θ(n log n) بغض النظر عن توزيع المدخلات.")
    elif strict_memory:
        if n <= 24 or prof["inversion_ratio"] <= 0.04:
            chosen = "insertion"
            reasons.append("حجم صغير أو شبه مرتب مع قيد ذاكرة O(1)؛ Insertion Sort أسرع عمليًا وأقل حركة ذاكرة.")
        else:
            chosen = "heap"
            reasons.append("Heap Sort يضمن أسوأ حالة Θ(n log n) داخل المصفوفة نفسها بذاكرة إضافية O(1) تمامًا.")
    else:
        if prof["duplicate_ratio"] >= 0.40 or prof["is_sorted"] or prof["is_reversed"]:
            chosen = "quick3"
            reasons.append("البيانات تحتوي تكرارات كثيرة أو مرتبة/معكوسة؛ Quick Sort الثلاثي (3-Way + Median-of-3) يعزل العناصر المتساوية في Θ(n) ويتفادى فخ Θ(n²).")
        elif prof["inversion_ratio"] <= 0.05 and n <= 300:
            chosen = "insertion"
            reasons.append("نسبة الانعكاسات (Inversions) منخفضة جدًا؛ Insertion Sort يكتفي بتمريرة سريعة قريبة من Θ(n).")
        else:
            chosen = "quick3"
            reasons.append("في البيانات العشوائية العامة، Quick Sort المحسّن (Median-of-3) يحقق سرعة عملية ممتازة بفضل محلية الذاكرة المخبئية (Cache Locality) وذاكرة O(log n).")

    if prof["is_sorted"] or prof["is_reversed"] or prof["duplicate_ratio"] >= 0.6:
        warnings.append("تحذير أكاديمي مهم: تجنب Quick Sort التقليدي (Last Pivot Lomuto) على هذه البيانات لأنه ينهار إلى أسوأ حالة Θ(n²).")

    return dict(
        profile=prof,
        recommended=chosen,
        recommended_meta=ALGORITHM_META[chosen],
        reasons=reasons,
        warnings=warnings,
    )


def render_advice_html(advice, bench_report=None):
    prof = advice["profile"]
    meta = advice["recommended_meta"]
    parts = [
        '<div class="aba-report" dir="rtl"><header class="aba-report-head">'
        '<span class="aba-kicker">مستشار اختيار الخوارزمية الذكي · Smart Algorithm Advisor</span>'
        f'<h2>التوصية الهندسية: {escape(meta["ar_name"])}</h2>'
        f'<p>تشخيص البيانات تلقائيًا: <b>{escape(prof["pattern_label"])}</b> | الحجم: {prof["n"]} عنصر</p></header>',
        '<div class="aba-stat-grid">',
        f'<div class="aba-stat"><small>نسبة الانعكاسات (Inversion Ratio)</small>'
        f'<strong>{prof["inversion_ratio"]*100:.1f}%</strong>'
        '<span>0% = مرتب تصاعديًا · 100% = مرتب تنازليًا · ~50% = عشوائي</span></div>',
        f'<div class="aba-stat"><small>نسبة التكرارات (Duplicate Ratio)</small>'
        f'<strong>{prof["duplicate_ratio"]*100:.1f}%</strong>'
        f'<span>عدد القيم الفريدة: {prof["unique_count"]} من {prof["n"]}</span></div>',
        f'<div class="aba-stat"><small>الخوارزمية الموصى بها</small>'
        f'<strong>{escape(meta["name"])}</strong>'
        f'<span>المتوسط: {meta["average"]} | المساحة: {meta["space"]}</span></div>',
        '</div>',
        '<section class="aba-insight"><h3>لماذا اختار المستشار هذه الخوارزمية؟</h3>',
    ]
    for r in advice["reasons"]:
        parts.append(f"<p>✅ {escape(r)}</p>")
    for w in advice["warnings"]:
        parts.append(f'<p style="color:#fde68a">⚠️ {escape(w)}</p>')
    parts.append("</section>")

    if bench_report:
        rows = sorted(bench_report["results"], key=lambda x: x["comparisons"])
        parts.append(
            '<section class="aba-panel"><h3>إثبات عملي فوري على بياناتك (مرتب حسب أقل المقارنات)</h3>'
            '<div class="aba-table-wrap"><table class="aba-table"><thead><tr>'
            '<th>الخوارزمية</th><th>المقارنات</th><th>الكتابات الكلية</th>'
            '<th>أقصى ذاكرة إضافية</th><th>وسيط الزمن (ms)</th></tr></thead><tbody>'
        )
        for r in rows:
            m = ALGORITHM_META[r["algorithm"]]
            badge = " ⭐ (الموصى بها)" if r["algorithm"] == advice["recommended"] else ""
            parts.append(
                f'<tr><th>{escape(m["name"] + badge)}</th>'
                f'<td dir="ltr">{r["comparisons"]:,}</td>'
                f'<td dir="ltr">{r["total_writes"]:,}</td>'
                f'<td dir="ltr">{r["max_aux_space"]:,}</td>'
                f'<td dir="ltr">{r["median_ns"]/1e6:.4f}</td></tr>'
            )
        parts.append("</tbody></table></div></section>")
    parts.append("</div>")
    return "".join(parts)


QUIZ_QUESTIONS = [
    {
        "q": "1. لماذا يرتفع عدد مقارنات Quick Sort (بمحور العنصر الأخير Lomuto) إلى 44,850 مقارنة عند ترتيب 300 عنصر مرتبة مسبقًا؟",
        "options": [
            "بسبب استهلاك ذاكرة إضافية بحجم O(n)",
            "لأن المحور يكون دائمًا أكبر عنصر فيقسّم القائمة إلى (n-1) و (0) في كل خطوة مما يؤدي إلى Θ(n²)",
            "لأن بايثون تعيد نسخ المصفوفة في كل تبديل",
        ],
        "correct": 1,
        "explanation": "عندما تكون المصفوفة مرتبة تصاعديًا ونختار العنصر الأخير محورًا، يفشل التقسيم المتوازن ويتحول مجموع المقارنات إلى n(n-1)/2 = 300×299/2 = 44,850 مقارنة.",
    },
    {
        "q": "2. أي خوارزمية مما يلي تجمع بين ضمان وقت Θ(n log n) في أسوأ حالة واستهلاك ذاكرة إضافية O(1) داخل المصفوفة؟",
        "options": [
            "Merge Sort",
            "Heap Sort",
            "Quick Sort (Last Pivot)",
        ],
        "correct": 1,
        "explanation": "Heap Sort يبني Max-Heap داخل نفس المصفوفة دون مخازن إضافية O(1) ويضمن سقف Θ(n log n) في أسوأ الحالات، بينما Merge Sort يحتاج O(n) ذاكرة إضافية.",
    },
    {
        "q": "3. إذا ضاعفنا حجم البيانات من n=400 إلى n=800 في خوارزمية ذات تعقيد Θ(n²)، فكم تقارب نسبة تضاعف العمليات C(2n)/C(n)؟",
        "options": [
            "حوالي 2.0",
            "حوالي 4.0",
            "حوالي 8.0",
        ],
        "correct": 1,
        "explanation": "في الخوارزميات التربيعية T(2n) / T(n) ≈ (2n)² / n² = 4.0، بينما في خوارزميات Θ(n log n) تكون النسبة قريبة من 2.1 إلى 2.2.",
    },
    {
        "q": "4. في شبكات الطرق الموزونة (حيث تختلف تكلفة العبور من خلية لأخرى)، أي خوارزمية تضمن إيجاد المسار الأقل تكلفة مع استكشاف أقل عدد من العقد؟",
        "options": [
            "Breadth-First Search (BFS)",
            "Depth-First Search (DFS)",
            "A* (A-Star) Search مع دالة استدلال مقبولة (Admissible Heuristic)",
        ],
        "correct": 2,
        "explanation": "خوارزمية A* تجمع بين التكلفة الفعلية g(n) مثل Dijkstra والتقدير الاستدلالي h(n) نحو الهدف، فتضمن الحل الأمثل مع تقليص فضاء البحث.",
    },
]


def grade_quiz(a0, a1, a2, a3):
    answers = [a0, a1, a2, a3]
    score = 0
    parts = [
        '<div class="aba-report" dir="rtl"><header class="aba-report-head">'
        '<span class="aba-kicker">نتيجة التقييم الذاتي للطالب</span>'
        '<h2>تصحيح الاختبار التفاعلي وتفسير الإجابات</h2></header>'
    ]
    for idx, item in enumerate(QUIZ_QUESTIONS):
        user_ans = answers[idx]
        correct_text = item["options"][item["correct"]]
        is_ok = user_ans == correct_text
        if is_ok:
            score += 1
        icon = "✅ إجابة صحيحة" if is_ok else "❌ إجابة غير دقيقة"
        parts.append(
            f'<section class="aba-panel" style="margin:10px 0"><h3>{escape(item["q"])}</h3>'
            f'<p><b>حالتك:</b> {icon} | <b>الإجابة النموذجية:</b> {escape(correct_text)}</p>'
            f'<p class="aba-hint">💡 <b>التفسير العلمي:</b> {escape(item["explanation"])}</p></section>'
        )
    parts.insert(
        1,
        f'<div class="aba-warning"><b>الدرجة النهائية: {score} من {len(QUIZ_QUESTIONS)} ({score*100//len(QUIZ_QUESTIONS)}%)</b> — '
        'جرب التحقق من هذه الحقائق عمليًا في تبويبات المقارنة ومنحنى النمو!</div>',
    )
    parts.append("</div>")
    return "".join(parts)
