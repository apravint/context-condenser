import unittest
from context_condenser.engine import condense

class TestCondenser(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(condense(""), "")

    def test_small_text_preserved(self):
        small = "Line 1\nLine 2\nLine 3"
        self.assertEqual(condense(small, max_lines=10), small)

    def test_compression_on_logs(self):
        # Generate 200 lines with a couple error lines
        lines = [f"Normal debug line {i}" for i in range(200)]
        lines[45] = "CRITICAL: Database connection failed abruptly"
        lines[110] = "FATAL: Out of memory exception in worker process"
        sample_log = "\n".join(lines)

        result = condense(sample_log, query="failed exception", max_lines=10, window=1)
        self.assertIn("Database connection failed abruptly", result)
        self.assertIn("Out of memory exception in worker process", result)
        self.assertIn("Context Condenser: Compressed", result)
        self.assertIn("lines compressed", result)

if __name__ == "__main__":
    unittest.main()
