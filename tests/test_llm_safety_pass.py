import unittest

from core.llm_client import ScriptedLLMClient
from core.llm_safety_pass import LLMSafetyPass
from core.patient_state import new_patient_state


class TestLLMSafetyPass(unittest.TestCase):
    def test_flags_emergency(self):
        client = ScriptedLLMClient(responses=[{"emergency_pattern_detected": True, "rationale": "atypical presentation of X"}])
        safety_pass = LLMSafetyPass(llm=client)
        flagged, rationale = safety_pass.check(new_patient_state("C1", "2026-08-21T00:00:00Z", "A1"))
        self.assertTrue(flagged)
        self.assertIn("atypical", rationale)

    def test_normal_case_not_flagged(self):
        client = ScriptedLLMClient(responses=[{"emergency_pattern_detected": False, "rationale": "no concerning pattern"}])
        safety_pass = LLMSafetyPass(llm=client)
        flagged, _ = safety_pass.check(new_patient_state("C1", "2026-08-21T00:00:00Z", "A1"))
        self.assertFalse(flagged)

    def test_prompt_includes_observed_facts_not_full_state(self):
        client = ScriptedLLMClient(responses=[{"emergency_pattern_detected": False, "rationale": "ok"}])
        safety_pass = LLMSafetyPass(llm=client)
        ps = new_patient_state("C1", "2026-08-21T00:00:00Z", "A1")
        ps["observed_facts"].append({"id": "F1", "variable": "heart_rate", "value": 130, "source": "device", "timestamp": "2026-08-21T00:00:00Z", "confidence": "high", "status": "observed"})
        safety_pass.check(ps)
        self.assertIn("heart_rate", client.calls[0]["user"])


if __name__ == "__main__":
    unittest.main()
