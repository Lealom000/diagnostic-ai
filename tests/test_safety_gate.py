import unittest

from core.safety_gate import SafetyState, combine_with_llm_pass, run_deterministic_safety_gate


def _ps(facts):
    return {"observed_facts": facts}


class TestDeterministicSafetyGate(unittest.TestCase):
    def test_normal_case_no_triggers(self):
        result = run_deterministic_safety_gate(_ps([{"variable": "oxygen_saturation", "value": 98}]))
        self.assertEqual(result.safety_state, SafetyState.NORMAL)
        self.assertEqual(result.triggered_rule_ids, [])

    def test_low_spo2_triggers_emergency(self):
        result = run_deterministic_safety_gate(_ps([{"variable": "oxygen_saturation", "value": 85}]))
        self.assertEqual(result.safety_state, SafetyState.EMERGENCY)
        self.assertIn("R-SPO2-CRIT", result.triggered_rule_ids)

    def test_altered_consciousness_triggers_emergency(self):
        result = run_deterministic_safety_gate(_ps([{"variable": "consciousness", "value": "unresponsive"}]))
        self.assertEqual(result.safety_state, SafetyState.EMERGENCY)
        self.assertIn("R-CONSCIOUSNESS-ALTERED", result.triggered_rule_ids)

    def test_non_numeric_spo2_value_does_not_crash(self):
        result = run_deterministic_safety_gate(_ps([{"variable": "oxygen_saturation", "value": "unknown"}]))
        self.assertEqual(result.safety_state, SafetyState.NORMAL)

    def test_deterministic_pass_is_idempotent(self):
        ps = _ps([{"variable": "bleeding_severity", "value": "major"}])
        r1 = run_deterministic_safety_gate(ps); r2 = run_deterministic_safety_gate(ps)
        self.assertEqual(r1.safety_state, r2.safety_state)
        self.assertEqual(r1.triggered_rule_ids, r2.triggered_rule_ids)


class TestCombineWithLlmPass(unittest.TestCase):
    def test_both_agree_normal(self):
        deterministic = run_deterministic_safety_gate(_ps([{"variable": "oxygen_saturation", "value": 98}]))
        self.assertEqual(combine_with_llm_pass(deterministic, llm_flagged_emergency=False).safety_state, SafetyState.NORMAL)

    def test_both_agree_emergency(self):
        deterministic = run_deterministic_safety_gate(_ps([{"variable": "oxygen_saturation", "value": 85}]))
        self.assertEqual(combine_with_llm_pass(deterministic, llm_flagged_emergency=True).safety_state, SafetyState.EMERGENCY)

    def test_disagreement_escalates_to_human_review_llm_flags_only(self):
        deterministic = run_deterministic_safety_gate(_ps([{"variable": "oxygen_saturation", "value": 98}]))
        combined = combine_with_llm_pass(deterministic, llm_flagged_emergency=True, llm_rationale="atypical presentation")
        self.assertEqual(combined.safety_state, SafetyState.HUMAN_REVIEW)

    def test_disagreement_escalates_to_human_review_deterministic_flags_only(self):
        deterministic = run_deterministic_safety_gate(_ps([{"variable": "oxygen_saturation", "value": 85}]))
        combined = combine_with_llm_pass(deterministic, llm_flagged_emergency=False)
        self.assertEqual(combined.safety_state, SafetyState.HUMAN_REVIEW)


if __name__ == "__main__":
    unittest.main()
