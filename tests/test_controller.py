import unittest

from core.controller import Decision, ToolCall, check


class TestController(unittest.TestCase):
    def test_read_only_allow_listed_tool_is_allowed(self):
        result = check(ToolCall(tool_name="evidence_search", is_write=False))
        self.assertEqual(result.decision, Decision.ALLOW)

    def test_unknown_read_tool_denied_by_default(self):
        result = check(ToolCall(tool_name="unknown_tool", is_write=False))
        self.assertEqual(result.decision, Decision.DENY)

    def test_write_tool_not_allow_listed_is_denied(self):
        result = check(ToolCall(tool_name="something_new", is_write=True))
        self.assertEqual(result.decision, Decision.DENY)

    def test_allow_listed_write_is_allowed(self):
        result = check(ToolCall(tool_name="audit_log_write", is_write=True))
        self.assertEqual(result.decision, Decision.ALLOW)

    def test_explicit_deny_list_wins_even_marked_read_only(self):
        result = check(ToolCall(tool_name="prescription", is_write=False))
        self.assertEqual(result.decision, Decision.DENY)

    def test_autonomous_treatment_always_denied(self):
        result = check(ToolCall(tool_name="autonomous_treatment", is_write=True))
        self.assertEqual(result.decision, Decision.DENY)


if __name__ == "__main__":
    unittest.main()
