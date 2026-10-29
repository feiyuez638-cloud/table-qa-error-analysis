"""生成报告配图。数字来自 diag_report.md 与报告第 6 节，不读比赛数据。"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": ["Microsoft YaHei", "SimHei", "sans-serif"],
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#52514e", "axes.labelcolor": "#0b0b0b",
    "xtick.color": "#52514e", "ytick.color": "#52514e",
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
})
BLUE, ORANGE, INK, MUTED = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e"
OUT = Path(__file__).resolve().parent.parent / "figures"
OUT.mkdir(exist_ok=True)


def rate_bars(rows, title, fname):
    """单序列横向条形：分歧率，条尾标注 分歧/总数。"""
    rows = sorted(rows, key=lambda r: r[1] / r[2])
    fig, ax = plt.subplots(figsize=(7, 0.55 * len(rows) + 1.2))
    ys = range(len(rows))
    ax.barh(ys, [s / n for _, s, n in rows], color=BLUE, height=0.6)
    for y, (_, s, n) in zip(ys, rows):
        ax.text(s / n + 0.01, y, f"{s}/{n}（{s / n:.0%}）", va="center", color=INK, fontsize=9)
    ax.set_yticks(list(ys), [r[0] for r in rows])
    ax.set_xlim(0, 1.05)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.grid(axis="x", color="#e5e4e0", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_title(title, loc="left", color=INK, fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / fname, dpi=160)
    plt.close(fig)


rate_bars([
    ("提取 / 文字", 97, 359), ("提取 / 数值", 23, 247), ("推理 / 数值", 4, 118),
    ("推理 / 数组", 22, 60), ("结构 / JSON", 31, 39),
], "图 1  各题型 × 答案格式的实质分歧率", "fig1_type_format.png")

rate_bars([
    ("jpg", 85, 330), ("png", 65, 328), ("pdf", 38, 240), ("webp（n=10）", 5, 10),
], "图 2  各文件类型的实质分歧率", "fig2_file_type.png")

# 图 3：干预实验修好 / 改坏（两序列，分组条形 + 直接标数）
exps = [
    ("结构规则 · dev", 16, 0), ("结构规则 · hold", 15, 0), ("规则有无 · hold3", 4, 0),
    ("三票众数", 0, 0), ("自一致投票 · hold3", 0, 1),
]
fig, ax = plt.subplots(figsize=(7, 3.6))
xs = range(len(exps))
w = 0.36
for off, idx, color, label in ((-w / 2, 1, BLUE, "修好"), (w / 2, 2, ORANGE, "改坏")):
    vals = [e[idx] for e in exps]
    ax.bar([x + off for x in xs], vals, width=w - 0.03, color=color, label=label)
    for x, v in zip(xs, vals):
        ax.text(x + off, v + 0.3, str(v), ha="center", color=INK, fontsize=9)
ax.set_xticks(list(xs), [e[0] for e in exps], fontsize=9)
ax.set_ylabel("题数")
ax.grid(axis="y", color="#e5e4e0", linewidth=0.8)
ax.set_axisbelow(True)
ax.legend(frameon=False, loc="upper right")
ax.set_title("图 3  干预实验的修好 / 改坏题数（离线验证集）", loc="left", color=INK, fontsize=11)
fig.tight_layout()
fig.savefig(OUT / "fig3_interventions.png", dpi=160)
plt.close(fig)
print("ok", sorted(p.name for p in OUT.glob("*.png")))
