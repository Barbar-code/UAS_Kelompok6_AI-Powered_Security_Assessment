import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import recon_agent
import summarize_runs


class ScopeValidationTests(unittest.TestCase):
    def test_accepts_local_dvwa_url_and_canonicalizes_loopback(self):
        self.assertEqual(
            recon_agent.assert_lab_target("127.0.0.1:8080/"),
            "http://127.0.0.1:8080",
        )

    def test_rejects_non_local_or_wrong_port_targets(self):
        for target in (
            "https://localhost:8080",
            "http://example.com:8080",
            "http://localhost:8000",
            "http://localhost:8080/vulnerabilities/",
            "http://user@localhost:8080",
        ):
            with self.subTest(target=target), self.assertRaises(recon_agent.LabScopeError):
                recon_agent.assert_lab_target(target)

    def test_ollama_server_must_be_local(self):
        self.assertEqual(
            recon_agent.assert_local_ollama_host("http://127.0.0.1:11434"),
            "http://127.0.0.1:11434",
        )
        with self.assertRaises(recon_agent.LabScopeError):
            recon_agent.assert_local_ollama_host("http://example.com:11434")

    def test_agent_rejects_remote_ollama_without_connecting(self):
        error_output = io.StringIO()
        with contextlib.redirect_stderr(error_output):
            result = recon_agent.main(["--host", "http://example.com:11434"])
        self.assertEqual(result, 2)
        self.assertIn("[DITOLAK]", error_output.getvalue())

    def test_dry_run_uses_only_the_local_target(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = recon_agent.main(
                    ["--dry-run", "--outdir", temp_dir, "--level", "low"]
                )
            prompts = list(Path(temp_dir).glob("*.prompt.txt"))
            self.assertEqual(result, 0)
            self.assertEqual(len(prompts), 1)
            prompt = prompts[0].read_text(encoding="utf-8")
            self.assertIn("http://localhost:8080", prompt)
            self.assertNotIn("172.20.0.0/24", prompt)


class SummaryOutputTests(unittest.TestCase):
    def test_per_tag_output_includes_table_and_ascii_charts(self):
        rows = [
            {"tag": "K1", "latency_s": 12.0, "tokens_per_second": 4.0, "eval_count": 48},
            {"tag": "K1", "latency_s": 8.0, "tokens_per_second": 6.0, "eval_count": 36},
            {"tag": "K2", "latency_s": 10.0, "tokens_per_second": 5.0, "eval_count": 50},
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "runs.jsonl"
            log_path.write_text(
                "\ufeff" + "\n".join(json.dumps(row) for row in rows),
                encoding="utf-8",
            )
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = summarize_runs.main(["--log", str(log_path), "--per-tag"])
            chart_path = Path(temp_dir) / "metrics-chart.svg"
            self.assertTrue(chart_path.is_file())
            self.assertIn("<svg", chart_path.read_text(encoding="utf-8"))

        self.assertEqual(result, 0)
        self.assertIn("| Tag | n | Latency rata-rata (s) |", output.getvalue())
        self.assertIn("Grafik: Latency rata-rata (detik)", output.getvalue())
        self.assertIn("Grafik: Kecepatan generasi rata-rata", output.getvalue())
        self.assertIn("K1", output.getvalue())

    def test_missing_metric_does_not_break_summary(self):
        rows = [{"tag": "K1", "latency_s": None, "tokens_per_second": None}]
        groups = summarize_runs.grouped_by_tag(rows)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            summarize_runs.print_tag_table(groups)
            summarize_runs.print_chart(groups)

        self.assertIn("| K1 | 1 | - | - | - |", output.getvalue())
        self.assertIn("Data metrik tidak tersedia.", output.getvalue())


if __name__ == "__main__":
    unittest.main()
