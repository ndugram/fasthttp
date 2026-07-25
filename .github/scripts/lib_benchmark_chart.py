"""
Render bench_results.json (produced by lib_benchmark.py) as lib_benchmark.png
— a clean, light comparison dashboard for the Telegram post.

Run:
    python .github/scripts/lib_benchmark_chart.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]

INK = "#0b0b0b"
INK_MUTED = "#52514e"
GRID = "#e7e5e0"
SURFACE = "#fcfcfb"
GREEN = "#1a8f4a"       # fasthttp — brand highlight
GRAY = "#b9b7ae"        # everything else — muted, de-emphasized
GRAY_MID = "#a5a299"
GRAY_DARK = "#8b8880"
CARD_BG = "#f4f3ef"
CARD_EDGE = "#e2e0d8"

DISPLAY_NAME = {
    "fasthttp": "fasthttp",
    "httpx": "httpx",
    "aiohttp": "aiohttp",
    "requests": "requests",
}

# fixed muted shade per non-highlighted library, so color still carries identity
OTHER_SHADES = {"aiohttp": GRAY, "httpx": GRAY_MID, "requests": GRAY_DARK}


def load_results(path: str = "bench_results.json") -> dict:
    with Path(path).open() as f:
        return json.load(f)


def _panel_title(ax, text: str) -> None:
    ax.set_title(text, fontsize=11, color=INK, fontweight="bold", loc="left", pad=10)


def _throughput_panel(fig, rect, rps: dict[str, float]) -> None:
    ax = fig.add_axes(rect)
    ax.set_facecolor(SURFACE)
    _panel_title(ax, "запросов в секунду")

    ordered = sorted(rps.items(), key=lambda kv: kv[1])
    names = [DISPLAY_NAME.get(k, k) for k, _ in ordered]
    values = np.array([v for _, v in ordered])
    colors = [GREEN if k == "fasthttp" else OTHER_SHADES.get(k, GRAY) for k, _ in ordered]

    y_pos = np.arange(len(names))
    ax.barh(y_pos, values, height=0.55, color=colors, zorder=3)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=10.5, color=INK)
    for label, (key, _) in zip(ax.get_yticklabels(), ordered, strict=True):
        if key == "fasthttp":
            label.set_fontweight("bold")
            label.set_color(GREEN)

    max_val = values.max()
    for y, v in zip(y_pos, values, strict=True):
        ax.text(
            v + max_val * 0.02, y, f"{v:,.0f}".replace(",", " "),
            va="center", ha="left", fontsize=9.5, color=INK, fontweight="bold",
            fontfamily="monospace",
        )

    ax.set_xlim(0, max_val * 1.24)
    ax.spines[:].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", colors=INK_MUTED, labelsize=7.5)
    ax.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)


def _share_donut_panel(fig, rect, rps: dict[str, float]) -> None:
    ax = fig.add_axes(rect)
    ax.set_facecolor(SURFACE)
    _panel_title(ax, "доля throughput")

    ordered = sorted(rps.items(), key=lambda kv: -kv[1])
    names = [DISPLAY_NAME.get(k, k) for k, _ in ordered]
    values = [v for _, v in ordered]
    colors = [GREEN if k == "fasthttp" else OTHER_SHADES.get(k, GRAY) for k, _ in ordered]
    total = sum(values)

    wedges, _ = ax.pie(
        values,
        colors=colors,
        startangle=90,
        counterclock=False,
        radius=0.9,
        wedgeprops={"width": 0.4, "edgecolor": SURFACE, "linewidth": 3},
    )

    for wedge, name, val in zip(wedges, names, values, strict=True):
        angle = (wedge.theta1 + wedge.theta2) / 2
        x = np.cos(np.radians(angle))
        y = np.sin(np.radians(angle))
        pct = val / total * 100
        is_fasthttp = name == "fasthttp"
        ax.annotate(
            f"{name}\n{pct:.0f}%",
            xy=(x * 0.65, y * 0.65),
            ha="center", va="center",
            fontsize=7.5,
            fontweight="bold" if is_fasthttp else "regular",
            color="white" if is_fasthttp else INK,
            annotation_clip=False,
        )

    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    ax.set_aspect("equal")


def _latency_panel(fig, rect, latency: dict[str, dict[str, float]]) -> None:
    ax = fig.add_axes(rect)
    ax.set_facecolor(SURFACE)
    _panel_title(ax, "медианная задержка запроса, мс")

    ordered = sorted(latency.items(), key=lambda kv: kv[1]["median_ms"])
    names = [DISPLAY_NAME.get(k, k) for k, _ in ordered]
    medians = np.array([v["median_ms"] for _, v in ordered])
    p95s = np.array([v["p95_ms"] for _, v in ordered])
    colors = [GREEN if k == "fasthttp" else OTHER_SHADES.get(k, GRAY) for k, _ in ordered]

    x_pos = np.arange(len(names))
    ax.bar(x_pos, medians, width=0.5, color=colors, zorder=3)
    ax.vlines(x_pos, medians, p95s, color=INK, linewidth=1.2, zorder=4)
    ax.scatter(x_pos, p95s, color=INK, s=26, zorder=5, marker="_", linewidth=2)

    for x, m, p in zip(x_pos, medians, p95s, strict=True):
        ax.text(
            x, p + p95s.max() * 0.05, f"{m:.0f}",
            ha="center", va="bottom", fontsize=9.5, color=INK, fontweight="bold",
            fontfamily="monospace",
        )

    ax.set_xticks(x_pos)
    ax.set_xticklabels(names, fontsize=10)
    for label, (key, _) in zip(ax.get_xticklabels(), ordered, strict=True):
        if key == "fasthttp":
            label.set_fontweight("bold")
            label.set_color(GREEN)

    ax.set_ylim(0, p95s.max() * 1.35)
    ax.spines[:].set_visible(False)
    ax.tick_params(axis="x", length=0)
    ax.tick_params(axis="y", colors=INK_MUTED, labelsize=7.5)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.text(
        1.0, 1.0, "— чёрточка = p95", transform=ax.transAxes, ha="right", va="bottom",
        fontsize=7, color=INK_MUTED,
    )


def _stat_cards_panel(fig, rect, data: dict) -> None:
    rps = data["requests_per_second"]
    fasthttp_rps = rps["fasthttp"]
    requests_rps = rps["requests"]
    aiohttp_rps = rps["aiohttp"]

    cards = [
        (f"{fasthttp_rps / requests_rps:.0f}×", "быстрее requests"),
        (f"{fasthttp_rps / aiohttp_rps * 100:.0f}%", "от throughput aiohttp"),
        (f"{data['requests']}", "запросов в тесте, concurrency " + str(data["concurrency"])),
    ]

    x0, y0, w, h = rect
    cell_h = h / len(cards)
    gap = cell_h * 0.12

    for i, (value, label) in enumerate(cards):
        cy0 = y0 + h - (i + 1) * cell_h + gap / 2
        cax = fig.add_axes((x0, cy0, w, cell_h - gap))
        cax.set_facecolor(CARD_BG)
        for spine in cax.spines.values():
            spine.set_edgecolor(CARD_EDGE)
            spine.set_linewidth(1)
        cax.set_xticks([])
        cax.set_yticks([])
        cax.text(
            0.5, 0.6, value, transform=cax.transAxes, ha="center", va="center",
            fontsize=18, fontweight="bold", color=GREEN, fontfamily="monospace",
        )
        cax.text(
            0.5, 0.24, label, transform=cax.transAxes, ha="center", va="center",
            fontsize=8, color=INK_MUTED,
        )


def make_chart(data: dict, out_path: str = "lib_benchmark.png") -> None:
    fig = plt.figure(figsize=(12, 9))
    fig.patch.set_facecolor(SURFACE)

    # --- logo + title -----------------------------------------------------
    logo_path = REPO_ROOT / "docs" / "logo.png"
    if logo_path.exists():
        logo_ax = fig.add_axes((0.035, 0.925, 0.045, 0.065))
        logo_ax.imshow(plt.imread(logo_path))
        logo_ax.axis("off")
        title_x = 0.095
    else:
        title_x = 0.035

    fig.text(title_x, 0.965, "fasthttp-client", fontsize=19, fontweight="bold", color=INK, ha="left", va="center")
    fig.text(
        title_x, 0.935,
        "скорость запросов — сравнение с другими HTTP-библиотеками",
        fontsize=10, color=INK_MUTED, ha="left", va="center",
    )
    fig.text(
        0.965, 0.955, "github.com/ndugram/fasthttp", fontsize=8.5,
        color=INK_MUTED, ha="right", va="center", fontfamily="monospace",
    )

    # --- 2x2-ish grid -------------------------------------------------------
    left, right = 0.06, 0.965
    top, bottom = 0.865, 0.11
    mid_x = 0.545
    mid_y = (top + bottom) / 2
    gap = 0.045

    _throughput_panel(fig, (left, mid_y + gap / 2, mid_x - left - gap / 2, top - mid_y - gap / 2), data["requests_per_second"])
    _latency_panel(fig, (left, bottom, mid_x - left - gap / 2, mid_y - bottom - gap / 2), data["latency"])

    donut_w = 0.24
    _share_donut_panel(fig, (mid_x + gap / 2, mid_y + gap / 2, donut_w, top - mid_y - gap / 2), data["requests_per_second"])
    cards_x = mid_x + gap / 2 + donut_w + 0.03
    _stat_cards_panel(fig, (cards_x, mid_y + gap / 2, right - cards_x, top - mid_y - gap / 2), data)

    stats_bottom_rect = (mid_x + gap / 2, bottom, right - mid_x - gap / 2, mid_y - bottom - gap / 2)
    ax = fig.add_axes(stats_bottom_rect)
    ax.set_facecolor(CARD_BG)
    for spine in ax.spines.values():
        spine.set_edgecolor(CARD_EDGE)
        spine.set_linewidth(1)
    ax.set_xticks([])
    ax.set_yticks([])
    fastest = max(data["requests_per_second"].items(), key=lambda kv: kv[1])[0]
    ax.text(
        0.5, 0.5,
        f"Локальный сервер · {data['requests']} запросов · concurrency {data['concurrency']}\n"
        f"имитация задержки реального API {data['simulated_latency_ms']:.0f}мс\n\n"
        f"Быстрее всех по сырому throughput: {DISPLAY_NAME.get(fastest, fastest)} — меньше слоёв поверх сокета.\n"
        "fasthttp добавляет валидацию, безопасность и логирование сверху httpx,\n"
        "оставаясь в том же порядке величины.",
        transform=ax.transAxes, ha="center", va="center", fontsize=8.5, color=INK_MUTED,
        linespacing=1.8,
    )

    plt.savefig(out_path, dpi=170, facecolor=SURFACE)
    plt.close()
    print(f"Saved {out_path}")


def main() -> None:
    data = load_results(sys.argv[1] if len(sys.argv) > 1 else "bench_results.json")
    make_chart(data)


if __name__ == "__main__":
    main()
