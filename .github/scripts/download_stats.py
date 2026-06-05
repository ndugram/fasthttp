"""
Fetch fasthttp-client download stats from pypistats.org + pepy.tech
and generate a bar chart saved as stats.png.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

matplotlib.use("Agg")

PACKAGE = "fasthttp-client"
GREEN = "#34D058"
BG = "#0d1117"
TEXT = "#e6edf3"
GRID = "#21262d"
DAYS = 30


def _fetch(url: str) -> dict:
    req = Request(url, headers={"User-Agent": "fasthttp-stats/1.0"})
    with urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def get_daily_downloads() -> tuple[list[str], list[int]]:
    """Return (dates, counts) for the last DAYS days from pypistats.org."""
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
    """Return all-time total from pepy.tech."""
    url = f"https://api.pepy.tech/api/v2/projects/{PACKAGE}"
    try:
        data = _fetch(url)
        return int(data.get("total_downloads", 0))
    except Exception:
        return 0


def format_num(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def make_chart(dates: list[str], counts: list[int], total: int) -> None:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    yesterday_downloads = counts[-1] if counts else 0

    short_dates = [d[5:] for d in dates]  # MM-DD

    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    bars = ax.bar(short_dates, counts, color=GREEN, width=0.7, zorder=3)


    if bars:
        bars[-1].set_color("#58e07a")
        bars[-1].set_edgecolor("#ffffff")
        bars[-1].set_linewidth(1.2)

    ax.set_title(
        f"📦 fasthttp-client — download stats ({today})",
        color=TEXT,
        fontsize=13,
        pad=14,
        fontweight="bold",
    )
    ax.set_xlabel("Date (last 30 days)", color=TEXT, fontsize=9, labelpad=8)
    ax.set_ylabel("Downloads / day", color=TEXT, fontsize=9, labelpad=8)

    ax.tick_params(colors=TEXT, labelsize=7.5)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: format_num(int(v))))


    for i, label in enumerate(ax.get_xticklabels()):
        label.set_visible(i % 5 == 0 or i == len(dates) - 1)

    ax.spines[:].set_color(GRID)
    ax.grid(axis="y", color=GRID, linewidth=0.6, zorder=0)


    stats_text = (
        f"Yesterday  {format_num(yesterday_downloads)}\n"
        f"All-time    {format_num(total)}"
    )
    ax.text(
        0.99,
        0.97,
        stats_text,
        transform=ax.transAxes,
        ha="right",
        va="top",
        color=TEXT,
        fontsize=9,
        fontfamily="monospace",
        bbox={"boxstyle": "round,pad=0.4", "facecolor": "#161b22", "edgecolor": GRID},
    )

    plt.tight_layout()
    plt.savefig("stats.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close()

    print(f"Chart saved. Yesterday: {yesterday_downloads}, Total: {total}")


def main() -> None:
    print("Fetching daily downloads...")
    dates, counts = get_daily_downloads()
    if not dates:
        print("No data returned from pypistats.org", file=sys.stderr)
        sys.exit(1)

    print("Fetching total downloads...")
    total = get_total_downloads()

    print(f"Got {len(dates)} days of data. Total: {total}")
    make_chart(dates, counts, total)


if __name__ == "__main__":
    main()
