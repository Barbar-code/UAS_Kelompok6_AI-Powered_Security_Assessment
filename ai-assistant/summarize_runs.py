#!/usr/bin/env python3
"""Cetak tabel metrik dan grafik ASCII dari ai-assistant/output/runs.jsonl.

Contoh:
    python ai-assistant/summarize_runs.py
    python ai-assistant/summarize_runs.py --per-tag
    python ai-assistant/summarize_runs.py --tag K1
    python ai-assistant/summarize_runs.py --format csv
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import statistics
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_LOG = BASE_DIR / "output" / "runs.jsonl"

COLUMNS = [
    ("timestamp", "Waktu"),
    ("tag", "Tag"),
    ("level", "Level"),
    ("latency_s", "Latency (s)"),
    ("first_token_s", "Token-1 (s)"),
    ("prompt_eval_s", "Prompt eval (s)"),
    ("eval_count", "Token"),
    ("tokens_per_second", "Token/s"),
    ("done_reason", "Selesai"),
]


def load(path: Path) -> list[dict]:
    if not path.is_file():
        raise SystemExit(f"Log tidak ditemukan: {path}")
    rows = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), 1
    ):
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"JSON tidak valid pada baris {line_number}: {exc}") from exc
        if not isinstance(item, dict):
            raise SystemExit(f"Data pada baris {line_number} harus berupa objek JSON.")
        rows.append(item)
    return rows


def cell(value) -> str:
    if value is None:
        return "-"
    return str(value).replace("|", r"\|").replace("\n", " ")


def numeric_values(items: list[dict], key: str) -> list[float]:
    values = []
    for item in items:
        value = item.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            values.append(float(value))
    return values


def grouped_by_tag(rows: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for row in rows:
        tag = str(row.get("tag") or "(tanpa tag)")
        groups.setdefault(tag, []).append(row)
    return groups


def print_run_table(rows: list[dict]) -> None:
    print("| " + " | ".join(name for _, name in COLUMNS) + " |")
    print("|" + "---|" * len(COLUMNS))
    for row in rows:
        print("| " + " | ".join(cell(row.get(key)) for key, _ in COLUMNS) + " |")


def print_tag_table(groups: dict[str, list[dict]]) -> None:
    print("| Tag | n | Latency rata-rata (s) | Token/s rata-rata | Token rata-rata |")
    print("|---|---:|---:|---:|---:|")
    for tag, items in groups.items():
        latency = numeric_values(items, "latency_s")
        throughput = numeric_values(items, "tokens_per_second")
        tokens = numeric_values(items, "eval_count")
        averages = (
            f"{statistics.mean(latency):.1f}" if latency else "-",
            f"{statistics.mean(throughput):.2f}" if throughput else "-",
            f"{statistics.mean(tokens):.0f}" if tokens else "-",
        )
        print(f"| {cell(tag)} | {len(items)} | {averages[0]} | {averages[1]} | {averages[2]} |")


def print_chart(groups: dict[str, list[dict]]) -> None:
    metrics = (
        ("latency_s", "Latency rata-rata (detik)"),
        ("tokens_per_second", "Kecepatan generasi rata-rata (token/detik)"),
    )
    width = 36
    label_width = min(24, max((len(tag) for tag in groups), default=8))

    for key, title in metrics:
        averages = []
        for tag, items in groups.items():
            values = numeric_values(items, key)
            if values:
                averages.append((tag, statistics.mean(values)))

        print(f"\nGrafik: {title}")
        if not averages:
            print("  Data metrik tidak tersedia.")
            continue

        maximum = max(value for _, value in averages)
        for tag, value in averages:
            bar_length = round(width * value / maximum) if maximum > 0 else 0
            bar = "#" * max(1, bar_length) if value > 0 else ""
            print(f"  {tag[:label_width]:<{label_width}} | {bar:<{width}} | {value:.2f}")


def write_svg_chart(groups: dict[str, list[dict]], path: Path) -> None:
    metrics = (
        ("latency_s", "Latensi rata-rata (detik)", "#2563eb"),
        ("tokens_per_second", "Kecepatan generasi rata-rata (token/detik)", "#059669"),
    )
    left = 250
    chart_width = 500
    row_height = 30
    section_height = 34 + len(groups) * row_height + 22
    height = 28 + len(metrics) * section_height
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{height}" '
        f'viewBox="0 0 900 {height}" role="img">',
        '<style>text{font-family:Arial,sans-serif;fill:#1f2937}.title{font-size:17px;font-weight:bold}.label{font-size:13px}.value{font-size:12px}</style>',
        '<rect width="100%" height="100%" fill="white"/>',
    ]
    y = 28
    for key, title, color in metrics:
        values = [
            (tag, statistics.mean(numbers))
            for tag, items in groups.items()
            if (numbers := numeric_values(items, key))
        ]
        elements.append(f'<text x="12" y="{y}" class="title">{html.escape(title)}</text>')
        y += 24
        if not values:
            elements.append(f'<text x="12" y="{y}" class="label">Data metrik tidak tersedia</text>')
            y += section_height - 24
            continue
        maximum = max(value for _, value in values)
        for tag, value in values:
            bar_width = round(chart_width * value / maximum) if maximum > 0 else 0
            elements.append(
                f'<text x="12" y="{y + 15}" class="label">{html.escape(tag)}</text>'
            )
            elements.append(
                f'<rect x="{left}" y="{y}" width="{bar_width}" height="20" '
                f'rx="3" fill="{color}"/>'
            )
            elements.append(
                f'<text x="{left + bar_width + 8}" y="{y + 15}" class="value">{value:.2f}</text>'
            )
            y += row_height
        y += 22
    elements.append("</svg>")
    path.write_text("\n".join(elements), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Cetak tabel metrik dan grafik ASCII dari runs.jsonl."
    )
    parser.add_argument("--log", default=str(DEFAULT_LOG), help="Path runs.jsonl")
    parser.add_argument("--tag", help="Hanya baris dengan tag ini (mis. K1)")
    parser.add_argument(
        "--exclude-tag", action="append", default=[], help="Buang tag tertentu"
    )
    parser.add_argument(
        "--per-tag", action="store_true", help="Tabel metrik dirata-ratakan per tag"
    )
    parser.add_argument(
        "--no-chart", action="store_true", help="Jangan cetak grafik ASCII"
    )
    parser.add_argument("--format", choices=("md", "csv"), default="md")
    args = parser.parse_args(argv)

    rows = load(Path(args.log))
    if args.tag:
        rows = [row for row in rows if str(row.get("tag")) == args.tag]
    for excluded in args.exclude_tag:
        rows = [row for row in rows if str(row.get("tag")) != excluded]

    if not rows:
        print("Tidak ada data yang cocok.")
        return 1

    if args.format == "csv":
        writer = csv.writer(sys.stdout, lineterminator="\n")
        writer.writerow([name for _, name in COLUMNS])
        for row in rows:
            writer.writerow([row.get(key) for key, _ in COLUMNS])
        return 0

    groups = grouped_by_tag(rows)
    if args.per_tag:
        print_tag_table(groups)
    else:
        print_run_table(rows)

    if not args.no_chart:
        print_chart(groups)
        chart_path = Path(args.log).resolve().parent / "metrics-chart.svg"
        write_svg_chart(groups, chart_path)
        print(f"\nGrafik SVG disimpan: {chart_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
