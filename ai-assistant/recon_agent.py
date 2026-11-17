#!/usr/bin/env python3
"""Recon & report-draft agent untuk lab DVWA (proyek Keamanan Informasi, Kelompok 6).

Alat ini TIDAK mengeksekusi perintah apa pun. Ia hanya:
  1. Memvalidasi bahwa target berada di dalam lab milik tim (guardrail etika).
  2. Menyusun prompt dari template di `ai-assistant/prompts/`.
  3. Mengirim prompt ke Ollama lokal (CPU-only) dan menyimpan jawabannya.
  4. Mencatat metrik ke `output/runs.jsonl` untuk bagian evaluasi AI.

Contoh pemakaian
----------------
    # 1. Uji prompt tanpa perlu Ollama berjalan
    python recon_agent.py --dry-run

    # 2. Jalankan dengan model lokal
    python recon_agent.py --model pentest-lab:3b --level low

    # 3. Draf laporan dari catatan bukti
    python recon_agent.py --mode report --scenario S2.1 --notes-file catatan-s21.txt

    # 4. Cek Ollama & model tersedia
    python recon_agent.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROMPT_DIR = BASE_DIR / "prompts"
DEFAULT_OUTPUT_DIR = BASE_DIR / "output"
RUNS_LOG = "runs.jsonl"

# --- Guardrail: hanya target lab yang diizinkan -----------------------------

LAB_HOSTNAMES = {"localhost", "127.0.0.1", "::1", "host.docker.internal"}
LAB_NETWORKS = (
    ipaddress.ip_network("172.20.0.0/24"),  # uas-lab-net (docs/topologi-lab.md)
    ipaddress.ip_network("127.0.0.0/8"),
)


class LabScopeError(RuntimeError):
    """Target berada di luar ruang lingkup lab."""


def normalize_target(raw: str) -> str:
    """Ubah input target menjadi URL kanonik http://host[:port]."""
    value = (raw or "").strip()
    if not value:
        raise LabScopeError("Target kosong. Contoh: --target http://localhost:8080")
    if "://" not in value:
        value = "http://" + value
    parts = urllib.parse.urlsplit(value)
    if not parts.hostname:
        raise LabScopeError(f"Target tidak valid: {raw!r}")
    return urllib.parse.urlunsplit(
        (parts.scheme or "http", parts.netloc, parts.path or "", "", "")
    )


def assert_lab_target(raw: str) -> str:
    """Pastikan target ada di dalam lab sendiri, bukan sistem pihak ketiga."""
    target = normalize_target(raw)
    host = urllib.parse.urlsplit(target).hostname or ""

    if host.lower() in LAB_HOSTNAMES:
        return target

    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        addr = None

    if addr is not None and any(addr in net for net in LAB_NETWORKS):
        return target

    raise LabScopeError(
        f"Target '{host}' berada di luar lab.\n"
        "Yang diizinkan hanya: localhost, 127.0.0.1, ::1, host.docker.internal,\n"
        "atau alamat di subnet lab 172.20.0.0/24 (lihat docs/topologi-lab.md).\n"
        "Proyek ini hanya menguji sistem milik tim sendiri."
    )


# --- Template prompt --------------------------------------------------------


def load_template(name: str) -> str:
    path = PROMPT_DIR / name
    if not path.is_file():
        raise FileNotFoundError(f"Template prompt tidak ditemukan: {path}")
    return path.read_text(encoding="utf-8")


def render(template: str, values: dict[str, str]) -> str:
    """Ganti placeholder {{KEY}}; gagal keras kalau ada placeholder tanpa nilai."""
    required = set(re.findall(r"\{\{\s*([A-Z_]+)\s*\}\}", template))
    missing = sorted(required - set(values))
    if missing:
        raise ValueError("Placeholder belum punya nilai: " + ", ".join(missing))
    out = template
    for key, value in values.items():
        out = out.replace("{{" + key + "}}", value)
        out = out.replace("{{ " + key + " }}", value)
    return out


# --- Klien Ollama -----------------------------------------------------------


def _get_json(url: str, timeout: float) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def list_models(host: str, timeout: float = 10.0) -> list[str]:
    data = _get_json(host.rstrip("/") + "/api/tags", timeout)
    return [m.get("name", "") for m in data.get("models", [])]


def generate(
    host: str,
    model: str,
    prompt: str,
    options: dict,
    timeout: float,
    stream: bool = True,
) -> tuple[str, dict]:
    """Kirim prompt ke /api/generate dan kembalikan (teks, metrik)."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream,
        "options": options,
    }
    req = urllib.request.Request(
        host.rstrip("/") + "/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    started = time.perf_counter()
    chunks: list[str] = []
    final: dict = {}

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        if not stream:
            final = json.loads(resp.read().decode("utf-8"))
            chunks.append(final.get("response", ""))
        else:
            for line in resp:
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line.decode("utf-8"))
                piece = item.get("response", "")
                if piece:
                    chunks.append(piece)
                    sys.stdout.write(piece)
                    sys.stdout.flush()
                if item.get("done"):
                    final = item
    if stream:
        sys.stdout.write("\n")
    latency = time.perf_counter() - started

    eval_ns = int(final.get("eval_duration") or 0)
    metrics = {
        "latency_s": round(latency, 3),
        "eval_count": final.get("eval_count"),
        "prompt_eval_count": final.get("prompt_eval_count"),
        "eval_duration_s": round(eval_ns / 1e9, 3) if eval_ns else None,
        "tokens_per_second": (
            round(final["eval_count"] / (eval_ns / 1e9), 2)
            if eval_ns and final.get("eval_count")
            else None
        ),
        "done_reason": final.get("done_reason"),
    }
    return "".join(chunks), metrics


# --- I/O hasil --------------------------------------------------------------


def write_run_log(outdir: Path, record: dict) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    with (outdir / RUNS_LOG).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def save_output(outdir: Path, stem: str, text: str) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / f"{stem}.md"
    path.write_text(text, encoding="utf-8")
    return path


# --- CLI --------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AI assistant (Ollama lokal) untuk recon DVWA di lab sendiri.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--mode",
        choices=("recon", "report"),
        default="recon",
        help="recon = rencana pemindaian (default); report = draf bagian laporan",
    )
    parser.add_argument(
        "--target",
        default="http://localhost:8080",
        help="URL target di dalam lab (default: http://localhost:8080)",
    )
    parser.add_argument(
        "--level",
        choices=("low", "medium", "high", "impossible"),
        default="low",
        help="Level keamanan DVWA (default: low)",
    )
    parser.add_argument(
        "--goal",
        default="Memetakan permukaan serangan DVWA dan menentukan modul yang diuji lebih dulu.",
        help="Tujuan sesi pengujian",
    )
    parser.add_argument(
        "--tools",
        default="nmap, curl, Burp Suite Community, browser (Firefox/Chrome)",
        help="Tool yang tersedia di mesin penyerang",
    )
    parser.add_argument("--notes", default="-", help="Catatan tambahan (teks bebas)")
    parser.add_argument(
        "--notes-file",
        help="File catatan/bukti untuk --mode report ('-' = stdin)",
    )
    parser.add_argument(
        "--scenario",
        default="S1",
        help="ID skenario untuk --mode report (mis. S2.1)",
    )
    parser.add_argument(
        "--model",
        default="pentest-lab:3b",
        help="Nama model Ollama (default: pentest-lab:3b)",
    )
    parser.add_argument(
        "--host",
        default="http://localhost:11434",
        help="Alamat server Ollama (default: http://localhost:11434)",
    )
    parser.add_argument(
        "--outdir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Folder hasil (default: ai-assistant/output)",
    )
    parser.add_argument("--temperature", type=float, default=0.3)
    parser.add_argument("--num-predict", type=int, default=700)
    parser.add_argument("--num-ctx", type=int, default=4096)
    parser.add_argument("--timeout", type=float, default=900.0)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Hanya cetak prompt yang akan dikirim (tanpa memanggil Ollama)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Cek koneksi Ollama dan ketersediaan model, lalu keluar",
    )
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Minta jawaban sekaligus (tanpa streaming)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass

    # 1. Guardrail target (berlaku untuk kedua mode).
    try:
        target = assert_lab_target(args.target)
    except LabScopeError as exc:
        print(f"[DITOLAK] {exc}", file=sys.stderr)
        return 2

    # 2. Opsional: cek Ollama.
    if args.check:
        try:
            models = list_models(args.host)
        except (urllib.error.URLError, OSError) as exc:
            print(f"[GAGAL] Ollama tidak bisa dihubungi di {args.host}: {exc}")
            print("Jalankan `ollama serve` lalu coba lagi.")
            return 3
        print(f"Ollama aktif di {args.host}")
        base = args.model.split(":")[0]
        hits = [m for m in models if m == args.model or m.split(":")[0] == base]
        print("Model tersedia:", ", ".join(models) if models else "(kosong)")
        print(f"Model diminta ({args.model}):", "ADA" if hits else "TIDAK ADA")
        if not hits:
            print(f"  → jalankan: ollama pull {args.model.split(':')[0]}")
        return 0 if hits else 4

    # 3. Siapkan konteks prompt.
    now = datetime.now()
    notes = args.notes
    if args.mode == "report":
        if not args.notes_file:
            print("[GAGAL] --mode report butuh --notes-file.", file=sys.stderr)
            return 1
        if args.notes_file == "-":
            notes = sys.stdin.read()
        else:
            path = Path(args.notes_file)
            if not path.is_file():
                print(f"[GAGAL] File catatan tidak ada: {path}", file=sys.stderr)
                return 1
            notes = path.read_text(encoding="utf-8-sig")
        if not notes.strip():
            print("[GAGAL] Catatan/bukti kosong; tidak ada dasar untuk menulis.", file=sys.stderr)
            return 1

    values = {
        "DATE": now.strftime("%Y-%m-%d %H:%M"),
        "TARGET": target,
        "LEVEL": args.level,
        "GOAL": args.goal,
        "TOOLS": args.tools,
        "MODEL": args.model,
        "NOTES": notes if notes.strip() and notes.strip() != "-" else "(tidak ada catatan tambahan)",
        "SCENARIO": args.scenario,
    }
    template_name = "recon-prompt.md" if args.mode == "recon" else "report-draft-prompt.md"
    prompt = render(load_template(template_name), values)

    outdir = Path(args.outdir)
    stem = f"{args.mode}-{now.strftime('%Y%m%d-%H%M%S')}"

    # 4. Dry run: simpan + cetak prompt saja.
    if args.dry_run:
        outdir.mkdir(parents=True, exist_ok=True)
        prompt_path = outdir / f"{stem}.prompt.txt"
        prompt_path.write_text(prompt, encoding="utf-8")
        print(prompt)
        print(f"\n---\n[DRY RUN] Prompt disimpan di: {prompt_path}")
        print(f"[DRY RUN] Panjang prompt: {len(prompt)} karakter. Ollama tidak dipanggil.")
        return 0

    # 5. Panggil Ollama.
    options = {
        "temperature": args.temperature,
        "num_predict": args.num_predict,
        "num_ctx": args.num_ctx,
    }
    print(f"[i] model={args.model} host={args.host} mode={args.mode} level={args.level}")
    try:
        answer, metrics = generate(
            host=args.host,
            model=args.model,
            prompt=prompt,
            options=options,
            timeout=args.timeout,
            stream=not args.no_stream,
        )
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:500]
        print(f"[GAGAL] Ollama menolak permintaan (HTTP {exc.code}): {detail}", file=sys.stderr)
        return 3
    except (urllib.error.URLError, OSError) as exc:
        print(f"[GAGAL] Tidak bisa menghubungi Ollama di {args.host}: {exc}", file=sys.stderr)
        print("Pastikan `ollama serve` berjalan dan model sudah di-pull.", file=sys.stderr)
        return 3

    if not answer.strip():
        print("[GAGAL] Jawaban kosong dari model.", file=sys.stderr)
        return 5

    # 6. Simpan jawaban + metrik.
    body = (
        f"<!-- mode={args.mode} model={args.model} target={target} "
        f"level={args.level} tanggal={now.isoformat(timespec='seconds')} -->\n\n"
        f"{answer.strip()}\n"
    )
    out_path = save_output(outdir, stem, body)

    record = {
        "timestamp": now.isoformat(timespec="seconds"),
        "mode": args.mode,
        "model": args.model,
        "target": target,
        "level": args.level,
        "scenario": args.scenario if args.mode == "report" else None,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16],
        "prompt_chars": len(prompt),
        "answer_chars": len(answer),
        "output_file": str(out_path.relative_to(BASE_DIR)) if out_path.is_relative_to(BASE_DIR) else str(out_path),
        **metrics,
    }
    write_run_log(outdir, record)

    print("\n---")
    print(f"[i] Jawaban disimpan di: {out_path}")
    print(f"[i] Latency: {metrics['latency_s']} s | "
          f"tokens/s: {metrics['tokens_per_second']} | "
          f"eval_count: {metrics['eval_count']}")
    print(f"[i] Metrik ditambahkan ke: {outdir / RUNS_LOG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
