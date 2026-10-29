import json, openpyxl, collections
import os
R = os.environ.get("TABLEQA_ROOT", ".").rstrip("/\\") + "/"  # 比赛工作目录，数据不随仓库公开
T = os.environ.get("TABLEQA_TESTS", R + "tests.xlsx")  # 官方题目表
ws = openpyxl.load_workbook(T, read_only=True).active
meta = {str(r[0]): r for r in ws.iter_rows(min_row=2, values_only=True)}
w = json.load(open("diag_classes.json", encoding="utf-8"))["worst"]
doc = collections.defaultdict(lambda: [0, 0]); fmt = collections.defaultdict(lambda: [0, 0]); ext = collections.defaultdict(lambda: [0, 0])
for i, m in meta.items():
    d = m[1]; s = w[i] == "sub"
    doc[d][0] += 1; doc[d][1] += s
    k = (m[2] if m[2] in ("extract","thinking","structure") else "?", m[5]); fmt[k][0] += 1; fmt[k][1] += s
    e = d.rsplit(".", 1)[-1].lower(); ext[e][0] += 1; ext[e][1] += s
print("文件类型:", {k: v for k, v in ext.items()})
print("题型×答案格式:", {f"{a}/{b}": v for (a, b), v in sorted(fmt.items(), key=lambda x: str(x))})
top = sorted(doc.items(), key=lambda x: -x[1][1])
print("文档数", len(doc), "有分歧文档", sum(1 for v in doc.values() if v[1]))
cum = 0; tot = sum(v[1] for v in doc.values())
for d, (n, s) in top[:30]:
    cum += s; print(d, f"{s}/{n}", f"累计{cum}/{tot}")
