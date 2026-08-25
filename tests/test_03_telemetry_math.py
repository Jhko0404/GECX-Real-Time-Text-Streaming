"""Section 3: Telemetry & Benchmark Mathematics (TC-08 ~ TC-10)."""

import unittest
import time
from bff.telemetry import TelemetryBenchmark

class TestSection03TelemetryMath(unittest.TestCase):
    def test_tc08_ttft_precision_calculation(self):
        """TC-08: Time-To-First-Token (TTFT) microsecond precision calculation."""
        benchmark = TelemetryBenchmark()
        time.sleep(0.04)  # 40ms simulated network latency
        benchmark.record_chunk("안녕하세요 ")
        
        telemetry = benchmark.finalize()
        self.assertIn("ttft_ms", telemetry)
        self.assertGreaterEqual(telemetry["ttft_ms"], 35.0)
        self.assertLessEqual(telemetry["ttft_ms"], 300.0)

    def test_tc09_tps_rolling_calculation(self):
        """TC-09: Tokens Per Second (TPS) throughput calculation."""
        benchmark = TelemetryBenchmark()
        time.sleep(0.02)
        benchmark.record_chunk("첫번째 단어 ")
        time.sleep(0.03)
        benchmark.record_chunk("두번째 단어 세번째 단어 네번째 단어")
        
        telemetry = benchmark.finalize()
        self.assertIn("tps", telemetry)
        self.assertGreaterEqual(telemetry["tps"], 5.0)

    def test_tc10_korean_utf8_token_estimation(self):
        """TC-10: Korean/English UTF-8 token count estimation."""
        benchmark = TelemetryBenchmark()
        sample_text = "안녕하세요, 고객님! 무엇을 도와드릴까요?"
        benchmark.record_chunk(sample_text)
        
        telemetry = benchmark.finalize()
        self.assertIn("total_tokens", telemetry)
        # 30 chars / 3.2 ~= 9 tokens
        self.assertGreaterEqual(telemetry["total_tokens"], 5)
        self.assertLessEqual(telemetry["total_tokens"], 20)

if __name__ == "__main__":
    unittest.main()
