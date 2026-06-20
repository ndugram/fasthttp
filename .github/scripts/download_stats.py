"""
Fetch fasthttp-client download stats from pypistats.org
and generate a line chart saved as stats.png.
"""

from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timedelta, timezone

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import requests
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import CubicSpline

matplotlib.use("Agg")

PACKAGE = "fasthttp-client"
GREEN = "#34D058"
GREEN_LIGHT = "#58e07a"
GREEN_DARK = "#1a6b2e"
TEAL = "#1f9e8c"
ORANGE = "#f0883e"
BG = "#0d1117"
BG_CARD = "#161b22"
BG_TOOLTIP = "#1c2333"
TEXT = "#e6edf3"
TEXT_MUTED = "#8b949e"
GRID = "#21262d"
ACCENT_LINE = "#30363d"
DAYS = 30


def _fetch(url: str, retries: int = 3) -> dict:
    for attempt in range(retries):
        resp = requests.get(url, headers={"User-Agent": "fasthttp-stats/1.0"}, timeout=15)
        if resp.status_code == 429:
            wait = 2 ** attempt * 5
            print(f"Rate limited, retrying in {wait}s...", file=sys.stderr)
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.json()
    msg = f"Failed after {retries} retries"
    raise RuntimeError(msg)


def get_daily_downloads() -> tuple[list[str], list[int]]:
    url = f"https://pypistats.org/api/packages/{PACKAGE}/overall?mirrors=false"
    data = _fetch(url)
    rows = sorted(data["data"], key=lambda r: r["date"])

    per_date: dict[str, int] = {}
    for row in rows:
        d = row["date"]
        per_date[d] = per_date.get(d, 0) + row["downloads"]
    dates = sorted(per_date)[-DAYS:]
    counts = [per_date[d] for d in dates]
    return dates, counts


def get_total_downloads() -> int:
    url = f"https://pepy.tech/projects/{PACKAGE}"
    try:
        resp = requests.get(url, headers={"User-Agent": "fasthttp-stats/1.0"}, timeout=15)
        resp.raise_for_status()
        import re
        match = re.search(r'totalDownloads[\\]*"\s*:\s*(\d+)', resp.text)
        if match:
            return int(match.group(1))
    except Exception as e:
        print(f"Failed to fetch total from pepy: {e}", file=sys.stderr)

    url = f"https://pypistats.org/api/packages/{PACKAGE}/overall?mirrors=false"
    try:
        data = _fetch(url)
        return sum(row["downloads"] for row in data["data"])
    except Exception as e:
        print(f"Failed to fetch total from pypistats: {e}", file=sys.stderr)
        return 0


def format_num(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def _gradient_fill(ax, x, y, color, alpha_max=0.18):
    cmap = LinearSegmentedColormap.from_list("grad", [(1, 1, 1, 0), color], N=256)
    ax.fill_between(x, y, alpha=alpha_max, color=color, zorder=2)
    ax.fill_between(x, y, alpha=alpha_max * 0.5, color=color, zorder=2)


def _add_glow(ax, x, y, color, linewidth=4, alpha=0.15):
    glow = ax.plot(x, y, color=color, linewidth=linewidth, alpha=alpha, zorder=3, solid_capstyle="round")
    return glow


def _peak_valley_annotations(ax, x, y, color):
    peaks = []
    valleys = []
    for i in range(1, len(y) - 1):
        if y[i] > y[i - 1] and y[i] > y[i + 1]:
            peaks.append(i)
        if y[i] < y[i - 1] and y[i] < y[i + 1]:
            valleys.append(i)

    for i in peaks[-3:]:
        ax.annotate(
            f"{format_num(int(y[i]))}",
            (x[i], y[i]),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            fontsize=6.5,
            color=TEXT_MUTED,
            fontfamily="monospace",
        )
    for i in valleys[:2]:
        ax.annotate(
            f"{format_num(int(y[i]))}",
            (x[i], y[i]),
            textcoords="offset points",
            xytext=(0, -14),
            ha="center",
            fontsize=6.5,
            color=TEXT_MUTED,
            fontfamily="monospace",
        )


def make_chart(dates: list[str], counts: list[int], total: int) -> tuple[int, int, int, int]:
    yesterday_downloads = counts[-1] if counts else 0
    week_downloads = sum(counts[-7:]) if len(counts) >= 7 else sum(counts)
    month_downloads = sum(counts)
    avg_daily = month_downloads // len(counts) if counts else 0

    x = [datetime.strptime(d, "%Y-%m-%d") for d in dates]
    y = np.array(counts, dtype=float)

    fig, ax = plt.subplots(figsize=(12, 5.5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    xs = np.linspace(mdates.date2num(x[0]), mdates.date2num(x[-1]), 300)
    cs = CubicSpline(mdates.date2num(x), y, bc_type="natural")
    ys = cs(xs)
    ys = np.clip(ys, 0, None)
    xs_dt = [mdates.num2date(t) for t in xs]

    _gradient_fill(ax, xs_dt, ys, GREEN)
    _add_glow(ax, xs_dt, ys, GREEN, linewidth=6, alpha=0.12)

    ax.plot(xs_dt, ys, color=GREEN, linewidth=2.5, solid_capstyle="round", zorder=4)
    ax.plot(xs_dt, ys, color=GREEN_LIGHT, linewidth=6, alpha=0.08, solid_capstyle="round", zorder=3)

    if len(y) >= 7:
        kernel = np.ones(7) / 7.0
        ma = np.convolve(y, kernel, mode="valid")
        ma_x = x[6:]
        ma_cs = CubicSpline(mdates.date2num(ma_x), ma, bc_type="natural")
        ma_xs = np.linspace(mdates.date2num(ma_x[0]), mdates.date2num(ma_x[-1]), 200)
        ma_ys = ma_cs(ma_xs)
        ma_xs_dt = [mdates.num2date(t) for t in ma_xs]
        ax.plot(ma_xs_dt, ma_ys, color=TEXT_MUTED, linewidth=1, linestyle="--", alpha=0.35, zorder=3)

    dots = ax.scatter(x, y, color=GREEN, s=18, zorder=5, edgecolors=BG, linewidth=0.8, alpha=0.5)
    ax.scatter([x[-1]], [y[-1]], color=GREEN_LIGHT, s=80, zorder=6, edgecolors=BG, linewidth=1.8)
    ax.scatter([x[-1]], [y[-1]], color="#ffffff", s=24, zorder=7, alpha=0.3)

    ax.annotate(
        f"{format_num(int(y[-1]))}",
        (x[-1], y[-1]),
        textcoords="offset points",
        xytext=(12, 8),
        ha="left",
        fontsize=7.5,
        color=GREEN_LIGHT,
        fontfamily="monospace",
        fontweight="bold",
    )

    ax.axvline(x=x[-1], color=ACCENT_LINE, linewidth=0.6, linestyle="--", zorder=1, alpha=0.5)

    _peak_valley_annotations(ax, x, y, TEXT_MUTED)

    start_str = dates[0]
    end_str = dates[-1]
    ax.set_title(
        "fasthttp-client  —  статистика загрузок",
        color=TEXT,
        fontsize=15,
        pad=12,
        fontweight="bold",
        loc="left",
    )
    ax.text(
        0.01,
        0.93,
        f"{start_str}  –  {end_str}",
        transform=ax.transAxes,
        color=TEXT_MUTED,
        fontsize=7.5,
        fontfamily="monospace",
        alpha=0.7,
    )

    ax.set_xlabel("")
    ax.set_ylabel("")

    ax.spines[:].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["left"].set_color(GRID)
    ax.spines["left"].set_linewidth(0.5)
    ax.spines["bottom"].set_visible(True)
    ax.spines["bottom"].set_color(GRID)
    ax.spines["bottom"].set_linewidth(0.5)

    ax.tick_params(colors=TEXT_MUTED, labelsize=7.5, length=3)
    ax.tick_params(axis="x", length=0)
    ax.yaxis.set_major_formatter(lambda v, _: format_num(int(v)))

    ax.grid(axis="y", color=GRID, linewidth=0.4, alpha=0.6, zorder=0)
    ax.set_axisbelow(True)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))

    for label in ax.get_xticklabels():
        label.set_ha("left")

    card_entries = [
        ("Вчера", format_num(yesterday_downloads)),
        ("За 7 дней", format_num(week_downloads)),
        ("За 30 дней", format_num(month_downloads)),
        ("В среднем", f"{format_num(avg_daily)}/д"),
        ("Всего", format_num(total)),
    ]

    card_lines = "\n".join(f"{label:<14} {val:>8}" for label, val in card_entries)
    ax.text(
        0.02,
        0.74,
        card_lines,
        transform=ax.transAxes,
        ha="left",
        va="top",
        color=TEXT,
        fontsize=8,
        fontfamily="monospace",
        linespacing=1.65,
        bbox={
            "boxstyle": "round,pad=0.6",
            "facecolor": BG_TOOLTIP,
            "edgecolor": ACCENT_LINE,
            "linewidth": 0.6,
        },
    )

    y_min = max(0, y.min() - y.max() * 0.05)
    y_max = y.max() if y.max() > 0 else 100
    ax.set_ylim(y_min, y_max * 1.35)
    ax.set_xlim(x[0] - timedelta(hours=6), x[-1] + timedelta(hours=18))

    fig.text(
        0.5,
        0.01,
        "Источник: pepy.tech  ·  pypistats.org",
        ha="center",
        color=TEXT_MUTED,
        fontsize=6.5,
        fontfamily="monospace",
        alpha=0.5,
    )

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.06)
    plt.savefig("stats.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close()

    print(
        f"Chart saved. Yesterday: {yesterday_downloads}, "
        f"Week: {week_downloads}, Month: {month_downloads}, "
        f"Avg: {avg_daily}, Total: {total}"
    )

    return yesterday_downloads, week_downloads, month_downloads, avg_daily


def main() -> None:
    print("Fetching daily downloads...")
    dates, counts = get_daily_downloads()
    if not dates:
        print("No data returned from pypistats.org", file=sys.stderr)
        sys.exit(1)

    print("Fetching total downloads...")
    total = get_total_downloads()

    print(f"Got {len(dates)} days of data. Total: {total}")
    yesterday, week, month, avg = make_chart(dates, counts, total)

    today = datetime.now(timezone.utc)
    date_str = today.strftime("%d.%m.%Y")

    outputs = {
        "date": date_str,
        "yesterday_downloads": str(yesterday),
        "week_downloads": str(week),
        "month_downloads": str(month),
        "avg_daily": str(avg),
        "total_downloads": str(total),
    }

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            for key, val in outputs.items():
                f.write(f"{key}={val}\n")
    else:
        for key, val in outputs.items():
            print(f"{key}={val}")


if __name__ == "__main__":
    main()
