import unittest

from core.llm_client import ScriptedLLMClient


class TestScriptedLLMClient(unittest.TestCase):
    def test_returns_responses_in_order(self):
        client = ScriptedLLMClient(responses=[{"a": 1}, {"a": 2}])
        self.assertEqual(client.complete_structured("sys", "u1", "tool", "desc", {}), {"a": 1})
        self.assertEqual(client.complete_structured("sys", "u2", "tool", "desc", {}), {"a": 2})

    def test_records_calls(self):
        client = ScriptedLLMClient(responses=[{"a": 1}])
        client.complete_structured("sys", "hello", "tool", "desc", {"type": "object"})
        self.assertEqual(len(client.calls), 1)
        self.assertEqual(client.calls[0]["user"], "hello")
        self.assertEqual(client.calls[0]["tool_name"], "tool")

    def test_raises_when_exhausted(self):
        client = ScriptedLLMClient(responses=[])
        with self.assertRaises(AssertionError):
            client.complete_structured("sys", "u", "tool", "desc", {})


if __name__ == "__main__":
    unittest.main()
