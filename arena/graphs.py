"""Graph & Grid Pathfinding Arena: BFS, DFS, Dijkstra, and A* Search."""
from collections import deque
import heapq
from html import escape
import random


GRAPH_META = {
    "bfs": {
        "name": "Breadth-First Search (BFS)",
        "ar_name": "البحث بالعرض أولًا (BFS)",
        "optimal_unweighted": True,
        "optimal_weighted": False,
        "complexity": "O(V + E)",
        "color": "#38bdf8",
    },
    "dfs": {
        "name": "Depth-First Search (DFS)",
        "ar_name": "البحث بالعمق أولًا (DFS)",
        "optimal_unweighted": False,
        "optimal_weighted": False,
        "complexity": "O(V + E)",
        "color": "#fb923c",
    },
    "dijkstra": {
        "name": "Dijkstra's Algorithm",
        "ar_name": "خوارزمية ديكسترا (Dijkstra)",
        "optimal_unweighted": True,
        "optimal_weighted": True,
        "complexity": "O((V + E) log V)",
        "color": "#a78bfa",
    },
    "astar": {
        "name": "A* (A-Star) Search",
        "ar_name": "خوارزمية A* الموجهة بالاستدلال",
        "optimal_unweighted": True,
        "optimal_weighted": True,
        "complexity": "O((V + E) log V) — موجهة بـ Manhattan Heuristic",
        "color": "#34d399",
    },
}


def generate_grid(rows=10, cols=14, preset="متاهة متوازنة", seed=42):
    """Generate a 2D grid where 0=blocked wall, 1=normal cell (cost 1), 3=heavy terrain (cost 3)."""
    rng = random.Random(int(seed))
    grid = [[1 for _ in range(cols)] for _ in range(rows)]
    start = (0, 0)
    goal = (rows - 1, cols - 1)
    for r in range(rows):
        for c in range(cols):
            if (r, c) in (start, goal):
                continue
            roll = rng.random()
            if preset == "متاهة متوازنة":
                if roll < 0.22:
                    grid[r][c] = 0
            elif preset == "تضاريس موزونة (تكلفة متغيرة)":
                if roll < 0.16:
                    grid[r][c] = 0
                elif roll < 0.48:
                    grid[r][c] = 3
            elif preset == "مفتوحة بلا عوائق":
                grid[r][c] = 1
            elif preset == "حاجز أوسط (اختبار الالتفاف)":
                if c == cols // 2 and 1 <= r <= rows - 2:
                    grid[r][c] = 0
                elif roll < 0.12:
                    grid[r][c] = 0
    # Guarantee start and goal neighbors are open so paths are usually feasible
    if cols > 1:
        grid[0][1] = 1
        grid[rows - 1][cols - 2] = 1
    if rows > 1:
        grid[1][0] = 1
        grid[rows - 2][cols - 1] = 1
    return dict(rows=rows, cols=cols, grid=grid, start=start, goal=goal, preset=preset, seed=seed)


def _neighbors(grid, r, c):
    rows, cols = len(grid), len(grid[0])
    for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 0:
            yield nr, nc, grid[nr][nc]


def _reconstruct(parent, start, goal):
    if goal not in parent:
        return []
    path = []
    curr = goal
    while curr is not None:
        path.append(curr)
        curr = parent[curr]
    path.reverse()
    return path if path and path[0] == start else []


def run_pathfinding(grid_spec, algorithm="astar"):
    if algorithm not in GRAPH_META:
        raise ValueError(f"Unknown graph algorithm: {algorithm}")
    grid = grid_spec["grid"]
    start = tuple(grid_spec["start"])
    goal = tuple(grid_spec["goal"])
    visited_order = []
    parent = {start: None}
    cost_so_far = {start: 0}

    if algorithm == "bfs":
        q = deque([start])
        seen = {start}
        while q:
            curr = q.popleft()
            visited_order.append(curr)
            if curr == goal:
                break
            for nr, nc, w in _neighbors(grid, *curr):
                nxt = (nr, nc)
                if nxt not in seen:
                    seen.add(nxt)
                    parent[nxt] = curr
                    cost_so_far[nxt] = cost_so_far[curr] + w
                    q.append(nxt)
    elif algorithm == "dfs":
        stack = [start]
        seen = set()
        while stack:
            curr = stack.pop()
            if curr in seen:
                continue
            seen.add(curr)
            visited_order.append(curr)
            if curr == goal:
                break
            # Reverse order so right/down are popped first
            for nr, nc, w in reversed(list(_neighbors(grid, *curr))):
                nxt = (nr, nc)
                if nxt not in seen:
                    parent[nxt] = curr
                    cost_so_far[nxt] = cost_so_far[curr] + w
                    stack.append(nxt)
    elif algorithm in ("dijkstra", "astar"):
        pq = [(0, 0, start)]
        closed = set()
        counter = 0
        while pq:
            _, _, curr = heapq.heappop(pq)
            if curr in closed:
                continue
            closed.add(curr)
            visited_order.append(curr)
            if curr == goal:
                break
            for nr, nc, w in _neighbors(grid, *curr):
                nxt = (nr, nc)
                new_cost = cost_so_far[curr] + w
                if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                    cost_so_far[nxt] = new_cost
                    parent[nxt] = curr
                    heuristic = (abs(goal[0] - nr) + abs(goal[1] - nc)) if algorithm == "astar" else 0
                    counter += 1
                    heapq.heappush(pq, (new_cost + heuristic, counter, nxt))

    path = _reconstruct(parent, start, goal)
    path_cost = sum(grid[r][c] for r, c in path[1:]) if path else None
    return dict(
        algorithm=algorithm,
        visited_order=visited_order,
        visited_count=len(visited_order),
        path=path,
        path_steps=max(0, len(path) - 1) if path else None,
        path_cost=path_cost,
        found=bool(path),
    )


def compare_pathfinding(preset="تضاريس موزونة (تكلفة متغيرة)", seed=42):
    spec = generate_grid(rows=10, cols=14, preset=preset, seed=int(seed))
    results = {name: run_pathfinding(spec, name) for name in GRAPH_META}
    return dict(spec=spec, results=results)


def render_grid_svg(spec, result):
    grid = spec["grid"]
    rows, cols = spec["rows"], spec["cols"]
    cell = 26
    w = cols * cell + 16
    h = rows * cell + 16
    visited_set = set(result["visited_order"])
    path_set = set(result["path"])
    start = tuple(spec["start"])
    goal = tuple(spec["goal"])

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="240">']
    for r in range(rows):
        for c in range(cols):
            x = 8 + c * cell
            y = 8 + r * cell
            val = grid[r][c]
            pos = (r, c)
            if val == 0:
                fill = "#0f172a"
            elif pos == start:
                fill = "#3b82f6"
            elif pos == goal:
                fill = "#ef4444"
            elif pos in path_set:
                fill = "#22c55e"
            elif pos in visited_set:
                fill = "#475569" if val == 1 else "#6d28d9"
            else:
                fill = "#1e293b" if val == 1 else "#312e81"
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell-2}" height="{cell-2}" rx="4" fill="{fill}" stroke="#334155" stroke-width="0.7"/>'
            )
            if pos == start:
                parts.append(f'<text x="{x+cell//2-1}" y="{y+cell//2+4}" text-anchor="middle" fill="white" font-size="11" font-weight="bold">S</text>')
            elif pos == goal:
                parts.append(f'<text x="{x+cell//2-1}" y="{y+cell//2+4}" text-anchor="middle" fill="white" font-size="11" font-weight="bold">G</text>')
            elif val == 3:
                parts.append(f'<text x="{x+cell//2-1}" y="{y+cell//2+4}" text-anchor="middle" fill="#c4b5fd" font-size="10">3</text>')
    parts.append("</svg>")
    return "".join(parts)


def render_pathfinding_battle(battle):
    spec = battle["spec"]
    results = battle["results"]
    parts = [
        f'<div class="aba-report" dir="rtl"><header class="aba-report-head">'
        f'<span class="aba-kicker">ساحة الرسوم البيانية وإيجاد المسارات · Graph Pathfinding Arena</span>'
        f'<h2>مقارنة BFS و DFS و Dijkstra و A* على نفس الشبكة</h2>'
        f'<p>النمط: {escape(spec["preset"])} | البذرة: {spec["seed"]} | الأبعاد: {spec["rows"]}×{spec["cols"]} '
        f'(خلية عادية = تكلفة 1، خلية بنفسجية رقم 3 = تكلفة 3، خلية داكنة = جدار عائق)</p></header>',
        '<div class="aba-legend">'
        '<span><i style="background:#3b82f6"></i>البداية (S)</span>'
        '<span><i style="background:#ef4444"></i>الهدف (G)</span>'
        '<span><i style="background:#22c55e"></i>المسار المختار</span>'
        '<span><i style="background:#475569"></i>عقد تم استكشافها (Visited)</span>'
        '<span><i style="background:#312e81"></i>تضاريس ثقيلة (تكلفة 3)</span>'
        '<span><i style="background:#0f172a"></i>جدار عائق</span>'
        '</div>',
        '<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:16px 0">',
    ]
    for key, meta in GRAPH_META.items():
        res = results[key]
        status = (
            f"التكلفة الكلية: {res['path_cost']} | طول المسار: {res['path_steps']} خطوة | استكشف: {res['visited_count']} عقدة"
            if res["found"]
            else f"لم يصل للهدف | استكشف: {res['visited_count']} عقدة"
        )
        parts.append(
            f'<section class="aba-panel"><h3>{escape(meta["ar_name"])}</h3>'
            f'<p class="aba-hint">{escape(status)}</p>'
            f'<div class="aba-chart" dir="ltr">{render_grid_svg(spec, res)}</div></section>'
        )
    parts.append("</div>")
    parts.append(
        '<section class="aba-panel"><h3>جدول المقارنة التحليلية لخوارزميات المسارات</h3>'
        '<div class="aba-table-wrap"><table class="aba-table"><thead><tr>'
        '<th>الخوارزمية</th><th>العقد المستكشفة (الأقل أسرع)</th><th>طول المسار (خطوات)</th>'
        '<th>تكلفة المسار الموزون (الأقل أفضل)</th><th>يضمن أقصر مسار موزون؟</th><th>التعقيد النظري</th></tr></thead><tbody>'
    )
    for key, meta in GRAPH_META.items():
        res = results[key]
        parts.append(
            f'<tr><th>{escape(meta["ar_name"])}</th>'
            f'<td dir="ltr">{res["visited_count"]}</td>'
            f'<td dir="ltr">{res["path_steps"] if res["found"] else "—"}</td>'
            f'<td dir="ltr">{res["path_cost"] if res["found"] else "—"}</td>'
            f'<td>{"نعم ✅" if meta["optimal_weighted"] else "لا ⚠️ (لغير الموزون فقط)" if meta["optimal_unweighted"] else "لا ❌"}</td>'
            f'<td dir="ltr">{escape(meta["complexity"])}</td></tr>'
        )
    parts.append(
        "</tbody></table></div></section>"
        '<section class="aba-insight"><h3>الخلاصة الأكاديمية للطالب</h3>'
        "<p>1. <b>A* Search</b> يستكشف عقدًا أقل من <b>Dijkstra</b> مع ضمان نفس المسار الأمثل تمامًا بفضل دالة الاستدلال (Manhattan Distance Heuristic).</p>"
        "<p>2. <b>BFS</b> يجد المسار الأقل في <i>عدد الخطوات</i>، لكنه في الشبكات الموزونة قد يمر عبر تضاريس ذات تكلفة (3) بدل الالتفاف بتكلفة أقل.</p>"
        "<p>3. <b>DFS</b> يندفع في اتجاه واحد بعمق، لذلك لا يضمن أقصر مسار أبدًا وغالباً ما ينتج مسارات متعرجة طويلة.</p></section></div>"
    )
    return "".join(parts)
