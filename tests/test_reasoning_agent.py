import unittest

from core.llm_client import ScriptedLLMClient
from core.patient_state import new_patient_state
from core.reasoning_agent import LLMReasoningAgent


class TestReasoningAgent(unittest.TestCase):
    def test_returns_hypotheses_from_model(self):
        scripted = {"hypotheses": [{"id": "H1", "diagnosis": "Community-acquired pneumonia", "supporting_findings": ["fever", "cough"], "contradicting_findings": [], "danger_level": "moderate", "current_confidence": "possible"}], "missing_information": [{"variable": "oxygen_saturation", "tier": 1, "rationale": "needed to assess severity"}], "uncertainty_notes": ["limited exam data"], "needs_more_information": True}
        agent = LLMReasoningAgent(ScriptedLLMClient(responses=[scripted]))
        result = agent.generate_hypotheses(new_patient_state("C1", "2026-08-21T00:00:00Z", "A1"))
        self.assertEqual(result["hypotheses"][0]["diagnosis"], "Community-acquired pneumonia")
        self.assertTrue(result["needs_more_information"])

    def test_boundary_strips_unauthorized_keys(self):
        scripted = {"hypotheses": [], "missing_information": [], "uncertainty_notes": [], "needs_more_information": False, "safety_state": "EMERGENCY", "review_state": "DIFFERENTIAL"}
        agent = LLMReasoningAgent(ScriptedLLMClient(responses=[scripted]))
        result = agent.generate_hypotheses(new_patient_state("C1", "2026-08-21T00:00:00Z", "A1"))
        self.assertNotIn("safety_state", result)
        self.assertNotIn("review_state", result)

    def test_prompt_includes_observed_facts(self):
        client = ScriptedLLMClient(responses=[{"hypotheses": [], "missing_information": [], "uncertainty_notes": [], "needs_more_information": False}])
        agent = LLMReasoningAgent(client)
        ps = new_patient_state("C1", "2026-08-21T00:00:00Z", "A1")
        ps["observed_facts"].append({"id": "F1", "variable": "temperature", "value": 39.1, "unit": "C", "source": "device", "timestamp": "2026-08-21T00:00:00Z", "confidence": "high", "status": "observed"})
        agent.generate_hypotheses(ps)
        self.assertIn("temperature", client.calls[0]["user"])
        self.assertIn("39.1", client.calls[0]["user"])


if __name__ == "__main__":
    unittest.main()
