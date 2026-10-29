"""零调用诊断：82.4 与历史独立运行逐题比较，把差异分成纯表示差异和实质差异。"""
import openpyxl, json, unicodedata, re, collections, sys
import os
R = os.environ.get("TABLEQA_ROOT", ".").rstrip("/\\") + "/"  # 比赛工作目录，数据不随仓库公开
T = os.environ.get("TABLEQA_TESTS", R + "tests.xlsx")  # 官方题目表
RUNS = {"v1_plus": "submission_v1_backup.xlsx", "tiles_plus": "submission_tiles.xlsx", "max38_mix": "submission_max38.xlsx"}

def load(p):
    ws = openpyxl.load_workbook(R + p, read_only=True).active
    return {str(r[0]): ("" if r[1] is None else str(r[1])) for r in ws.iter_rows(min_row=2, values_only=True)}

def num(s):
    s = str(s).strip()
    if re.fullmatch(r"-?[\d,]*\.?\d+", s):
        try: return float(s.replace(",", ""))
        except ValueError: return None
    return None

def eq_scalar(a, b):
    """纯表示等价：外侧空白、数值等价（0.30=0.3，千分位）。"""
    a, b = str(a).strip(), str(b).strip()
    if a == b: return True
    na, nb = num(a), num(b)
    return na is not None and nb is not None and na == nb

def jparse(s):
    try: return json.loads(s)
    except Exception: return None

def cells_key(o):
    return sorted((c.get("row"), c.get("col"), c.get("rowspan"), c.get("colspan"), str(c.get("text", "")).strip()) for c in o.get("cells", []))

def classify(a, b, qt):
    if a == b: return "same"
    if a.strip() == b.strip(): return "repr:空白"
    ja, jb = jparse(a), jparse(b)
    if qt == "structure" and isinstance(ja, dict) and isinstance(jb, dict):
        if (ja.get("row_count"), ja.get("col_count"), cells_key(ja)) == (jb.get("row_count"), jb.get("col_count"), cells_key(jb)):
            return "repr:JSON顺序"
        return "sub:结构"
    if isinstance(ja, list) and isinstance(jb, list):
        if len(ja) == len(jb) and all(eq_scalar(x, y) for x, y in zip(ja, jb)): return "repr:数组数值"
        return "sub:数组"
    if isinstance(ja, dict) and isinstance(jb, dict) and ja == jb: return "repr:JSON顺序"
    if eq_scalar(a, b): return "repr:数值"
    # 以下不算无损，单列
    if a.strip().lower() == b.strip().lower(): return "soft:大小写"
    if unicodedata.normalize("NFKC", a).strip() == unicodedata.normalize("NFKC", b).strip(): return "soft:全半角"
    yn = {"yes": "是", "no": "否"}
    if yn.get(a.strip().lower()) == b.strip() or yn.get(b.strip().lower()) == a.strip(): return "soft:是否翻译"
    return "sub:标量"

ws = openpyxl.load_workbook(T, read_only=True).active
meta = {str(r[0]): r for r in ws.iter_rows(min_row=2, values_only=True)}
qt = {i: (m[2] if m[2] in ("extract", "thinking", "structure") else "extract?") for i, m in meta.items()}
base = load("submission_full_max_20261005.xlsx")
runs = {k: load(v) for k, v in RUNS.items()}

out = {}
for i in base:
    cls = {k: classify(base[i], r[i], qt[i]) for k, r in runs.items()}
    out[i] = cls
# 单版本分歧（原始字符串不同）与各类计数
for k in runs:
    c = collections.Counter(out[i][k] for i in base)
    print(k, "原始不同", sum(v for kk, v in c.items() if kk != "same"), dict(c))
def worst(cls):
    v = list(cls.values())
    for p in ("sub:", "soft:", "repr:"):
        if any(x.startswith(p) for x in v): return p[:-1]
    return "same"
w = {i: worst(out[i]) for i in base}
tab = collections.defaultdict(collections.Counter)
for i in base: tab[qt[i]][w[i]] += 1
print("按题型（取各版本最重的差异）:", {k: dict(v) for k, v in tab.items()})
json.dump({"per_id": out, "worst": w}, open("diag_classes.json", "w", encoding="utf-8"), ensure_ascii=False)
