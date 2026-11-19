#!/usr/bin/env python3
"""Rangkum ai-assistant/output/runs.jsonl menjadi tabel Markdown.

Dipakai untuk mengisi bagian 7 `docs/evaluasi-ai.md`. Hanya memakai standard
library, sama seperti `recon_agent.py`.

Contoh:
    python ai-assistant/summarize_runs.py                 # semua run
    python ai-assistant/summarize_runs.py --tag K1        # hanya tag K1
    python ai-assistant/summarize_runs.py --per-tag       # rata-rata per tag
    python ai-assistant/summarize_runs.py --format csv    # untuk Excel
"""

from __future__ import annotations

import argparse
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
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def cell(value) -> str:
    if value is None:
        return "-"
    return str(value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rangkum runs.jsonl jadi tabel.")
    parser.add_argument("--log", default=str(DEFAULT_LOG), help="Path runs.jsonl")
    parser.add_argument("--tag", help="Hanya baris dengan tag ini (mis. K1)")
    parser.add_argument("--exclude-tag", action="append", default=[], help="Buang tag tertentu")
    parser.add_argument("--per-tag", action="store_true", help="Tampilkan rata-rata per tag")
    parser.add_argument("--format", choices=("md", "csv"), default="md")
    args = parser.parse_args(argv)

    rows = load(Path(args.log))
    if args.tag:
        rows = [r for r in rows if str(r.get("tag")) == args.tag]
    for bad in args.exclude_tag:
        rows = [r for r in rows if str(r.get("tag")) != bad]

    if not rows:
        print("Tidak ada data yang cocok.")
        return 1

    if args.format == "csv":
        print(",".join(name for name, _ in COLUMNS))
        for r in rows:
            print(",".join(cell(r.get(key)) for key, _ in COLUMNS))
        return 0

    if args.per_tag:
        groups: dict[str, list[dict]] = {}
        for r in rows:
            groups.setdefault(str(r.get("tag") or "(tanpa tag)"), []).append(r)
        print("| Tag | n | Latency rata-rata (s) | Token/s rata-rata | Token rata-rata |")
        print("|---|---|---|---|---|")
        for tag, items in groups.items():
            lat = [i["latency_s"] for i in items if i.get("latency_s") is not None]
            tps = [i["tokens_per_second"] for i in items if i.get("tokens_per_second")]
            tok = [i["eval_count"] for i in items if i.get("eval_count")]
            print(
                f"| {tag} | {len(items)} | "
                f"{statistics.mean(lat):.1f} | "
                f"{statistics.mean(tps):.2f} | "
                f"{statistics.mean(tok):.0f} |"
            )
        return 0

    print("| " + " | ".join(name for _, name in COLUMNS) + " |")
    print("|" + "---|" * len(COLUMNS))
    for r in rows:
        print("| " + " | ".join(cell(r.get(key)) for key, _ in COLUMNS) + " |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
