"""
Olist e-commerce analysis: runs every SQL file in sql/, saves results and charts.
Olist 电商分析：运行 sql/ 下所有查询，保存结果表和图表。

Usage / 用法:  python src/run_analysis.py   (run from the project root / 在项目根目录运行)
"""
from pathlib import Path

import duckdb
import matplotlib
matplotlib.use("Agg")  # no window needed / 不弹出窗口，直接存图
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "sql"
OUT_DIR = ROOT / "reports"
FIG_DIR = OUT_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

INK, MUTED, ACCENT, ALERT = "#1f2933", "#9aa5b1", "#2f6fdb", "#d64545"
plt.rcParams.update({
    "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
})


def run_queries() -> dict[str, pd.DataFrame]:
    con = duckdb.connect()
    # paths in SQL are relative to the project root / SQL 里的路径相对于项目根目录
    con.execute(f"SET file_search_path = '{ROOT.as_posix()}'")
    con.execute((SQL_DIR / "00_setup_views.sql").read_text())
    results = {}
    for f in sorted(SQL_DIR.glob("0[1-9]_*.sql")):
        df = con.sql(f.read_text()).df()
        df.to_csv(OUT_DIR / f"{f.stem}.csv", index=False)
        results[f.stem] = df
    return results


def chart_growth(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.plot(df["month"], df["orders"], color=ACCENT, lw=2)
    peak = df.loc[df["orders"].idxmax()]
    ax.annotate(f"Black Friday\n{peak['orders']:,} orders",
                xy=(peak["month"], peak["orders"]), xytext=(-95, -10),
                textcoords="offset points", color=INK,
                arrowprops=dict(arrowstyle="-", color=MUTED))
    ax.set_title("Orders grew fast in 2017, then flattened in 2018", loc="left", color=INK)
    ax.set_ylabel("Delivered orders / month")
    ax.grid(axis="y", color="#e4e7eb")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "01_monthly_orders.png", dpi=160)
    plt.close(fig)


def chart_delay(df: pd.DataFrame) -> None:
    labels = ["On time", "1–3 days\nlate", "4–7 days\nlate", "8–14 days\nlate", "15+ days\nlate"]
    colors = [ACCENT] + [ALERT] * 4
    fig, ax = plt.subplots(figsize=(8, 3.6))
    bars = ax.bar(labels, df["avg_review"], color=colors, width=0.6)
    for b, v, n in zip(bars, df["avg_review"], df["pct_orders"]):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.08, f"{v:.2f}", ha="center", color=INK)
        ax.text(b.get_x() + b.get_width() / 2, 0.15, f"{n:.1f}% of\norders",
                ha="center", color="white", fontsize=8)
    ax.set_ylim(0, 5)
    ax.set_ylabel("Average review score (1–5)")
    ax.set_title("Even 1–3 days late costs a full star", loc="left", color=INK)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "02_delay_vs_review.png", dpi=160)
    plt.close(fig)


def chart_states(df: pd.DataFrame) -> None:
    df = df.sort_values("late_rate_pct")
    fig, ax = plt.subplots(figsize=(8, 4.8))
    # label each bar with order volume, so the reader sees where late orders actually pile up
    ax.barh(df["customer_state"], df["late_rate_pct"],
            color=[ALERT if s == "RJ" else ACCENT if s == "SP" else MUTED for s in df["customer_state"]])
    for y, (rate, n) in enumerate(zip(df["late_rate_pct"], df["orders"])):
        ax.text(rate + 0.3, y, f"{rate:.1f}%  ({n:,} orders)", va="center", fontsize=8, color=INK)
    ax.set_xlabel("Share of orders delivered after the estimated date (%)")
    ax.set_xlim(0, df["late_rate_pct"].max() * 1.45)
    rates = df.set_index("customer_state")["late_rate_pct"]
    ax.set_title(f"Rio de Janeiro (red) is late {rates['RJ'] / rates['SP']:.1f}x as often as São Paulo (blue)",
                 loc="left", color=INK)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "03_late_rate_by_state.png", dpi=160)
    plt.close(fig)


def chart_first_review(df: pd.DataFrame, overall_pct: float) -> None:
    fig, ax = plt.subplots(figsize=(8, 3.6))
    labels = [f"{int(s)}★" for s in df["first_order_review"]]
    bars = ax.bar(labels, df["repeat_rate_pct"], color=MUTED, width=0.6)
    bars[0].set_color(ALERT)
    bars[-1].set_color(ACCENT)
    for b, v, n in zip(bars, df["repeat_rate_pct"], df["customers"]):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.3, f"{v:.1f}%", ha="center", color=INK)
        ax.text(b.get_x() + b.get_width() / 2, 0.2, f"{n:,}\ncustomers",
                ha="center", color="white", fontsize=8)
    ax.axhline(overall_pct, color=INK, lw=1, ls="--")
    ax.text(len(df) - 0.5, 4.7, f"dashed line = all customers ({overall_pct:.1f}%)",
            ha="right", fontsize=8, color=INK)
    ax.set_ylim(0, 5)
    ax.set_xlabel("Review score of the customer's first order")
    ax.set_ylabel("Customers who ordered again (%)")
    ax.set_title("A 1-star first order and a 5-star one lead to almost the same repeat rate",
                 loc="left", color=INK)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "04_first_review_vs_repeat.png", dpi=160)
    plt.close(fig)


def chart_categories(df: pd.DataFrame) -> None:
    df = df.sort_values("gmv_brl")
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.barh(df["category"].str.replace("_", " "), df["gmv_brl"] / 1e6, color=ACCENT)
    for y, (gmv, rv) in enumerate(zip(df["gmv_brl"] / 1e6, df["avg_review"])):
        ax.text(gmv + 0.02, y, f"R${gmv:.2f}M · {rv:.2f}★", va="center", fontsize=8, color=INK)
    ax.set_xlabel("GMV, million BRL (item price + freight)")
    ax.set_xlim(0, df["gmv_brl"].max() / 1e6 * 1.3)
    ax.set_title("Top 10 categories by GMV: health & beauty leads", loc="left", color=INK)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "05_top_categories.png", dpi=160)
    plt.close(fig)


def headline_numbers(r: dict[str, pd.DataFrame]) -> None:
    g = r["01_growth"].copy()
    g["year"] = pd.to_datetime(g["month"]).dt.year
    jan_aug = g[pd.to_datetime(g["month"]).dt.month <= 8].groupby("year")["orders"].sum()
    d = r["02_delivery_vs_review"]
    s = r["03_late_by_state"].set_index("customer_state")
    rj, sp = s.loc["RJ"], s.loc["SP"]
    rj_avoidable = rj["orders"] * (rj["late_rate_pct"] - sp["late_rate_pct"]) / 100
    rep = r["04_repeat_purchase"].iloc[0]
    print("\n=== Headline numbers / 关键数字 ===")
    print(f"Jan–Aug orders: 2017 = {jan_aug[2017]:,}, 2018 = {jan_aug[2018]:,} "
          f"(+{jan_aug[2018] / jan_aug[2017] - 1:.0%} YoY)")
    print(f"Late orders: {100 - d.iloc[0]['pct_orders']:.1f}% of delivered orders")
    print(f"Review: on time {d.iloc[0]['avg_review']:.2f} vs 1–3 days late {d.iloc[1]['avg_review']:.2f}")
    print(f"RJ late orders avoidable if RJ matched SP's late rate: ~{rj_avoidable:,.0f}")
    print(f"Repeat purchase rate: {rep['repeat_rate_pct']:.1f}% of {int(rep['customers']):,} customers")


if __name__ == "__main__":
    res = run_queries()
    chart_growth(res["01_growth"])
    chart_delay(res["02_delivery_vs_review"])
    chart_states(res["03_late_by_state"])
    chart_first_review(res["05_first_review_vs_repeat"],
                       float(res["04_repeat_purchase"].iloc[0]["repeat_rate_pct"]))
    chart_categories(res["06_top_categories"])
    headline_numbers(res)
    print(f"\nSaved tables to {OUT_DIR} and charts to {FIG_DIR}")
