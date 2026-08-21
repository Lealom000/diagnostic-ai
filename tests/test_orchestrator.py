import os
import tempfile
import unittest

from core.audit_log import AuditLog
from core.evidence_tool import EvidenceTool
from core.llm_client import ScriptedLLMClient
from core.llm_safety_pass import LLMSafetyPass
from core.orchestrator import Orchestrator
from core.patient_state import new_patient_state
from core.reasoning_agent import LLMReasoningAgent
from core.safety_gate import SafetyState


class FakeBackend:
    def __init__(self, results):
        self._results = results

    def search(self, query):
        return self._results


class TestOrchestratorIntegration(unittest.TestCase):
    def setUp(self):
        self.log_path = tempfile.mktemp()
        self.audit_log = AuditLog(self.log_path)

    def tearDown(self):
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

    def _orchestrator(self, safety_responses, reasoning_responses, evidence_responses, backend_results=None):
        return Orchestrator(
            audit_log=self.audit_log,
            reasoning_agent=LLMReasoningAgent(ScriptedLLMClient(responses=reasoning_responses)),
            evidence_tool=EvidenceTool(backend=FakeBackend(backend_results or []), llm=ScriptedLLMClient(responses=evidence_responses)),
            llm_safety_pass=LLMSafetyPass(ScriptedLLMClient(responses=safety_responses)),
        )

    def test_full_wiring_normal_case(self):
        orch = self._orchestrator(
            safety_responses=[{"emergency_pattern_detected": False, "rationale": "ok"}],
            reasoning_responses=[{"hypotheses": [{"id": "H1", "diagnosis": "Viral URI", "supporting_findings": ["cough"], "contradicting_findings": [], "danger_level": "low", "current_confidence": "likely"}], "missing_information": [], "uncertainty_notes": [], "needs_more_information": False}],
            evidence_responses=[],
        )
        ps = new_patient_state("INT-1", "2026-08-21T00:00:00Z", "AUD-1")
        ps["observed_facts"].append({"id": "F1", "variable": "oxygen_saturation", "value": 98, "source": "device", "timestamp": "2026-08-21T00:00:00Z", "confidence": "high", "status": "observed"})
        self.assertEqual(orch.run_safety_check(ps, "INT-1"), SafetyState.NORMAL)
        self.assertEqual(orch.run_reasoning_step(ps, "INT-1")["hypotheses"][0]["diagnosis"], "Viral URI")
        event_types = [r["event_type"] for r in self.audit_log.read_all("INT-1")]
        self.assertIn("safety_check", event_types)
        self.assertIn("reasoning_step", event_types)

    def test_disagreement_escalates(self):
        orch = self._orchestrator(
            safety_responses=[{"emergency_pattern_detected": False, "rationale": "disagree with rule engine"}], reasoning_responses=[], evidence_responses=[]
        )
        ps = new_patient_state("INT-2", "2026-08-21T00:00:00Z", "AUD-2")
        ps["observed_facts"].append({"id": "F1", "variable": "oxygen_saturation", "value": 82, "source": "device", "timestamp": "2026-08-21T00:00:00Z", "confidence": "high", "status": "observed"})
        self.assertEqual(orch.run_safety_check(ps, "INT-2"), SafetyState.HUMAN_REVIEW)

    def test_next_step_selection_is_deterministic_no_llm_needed(self):
        orch = self._orchestrator([], [], [])
        ranked = orch.run_next_step_selection([{"variable": "travel_history", "tier": 4}, {"variable": "oxygen_saturation", "tier": 0}])
        self.assertEqual(ranked[0]["variable"], "oxygen_saturation")

    def test_evidence_retrieval_logs_to_audit(self):
        orch = self._orchestrator([], [], [{"claim_supported": "supports", "retrieved_text_summary": "S."}], [{"domain": "cdc.gov", "source": "CDC", "title": "T", "date": "2026", "snippet": "s", "url": "u"}])
        self.assertEqual(len(orch.run_evidence_retrieval("claim", "H1", "INT-3", patient_state_version=1)), 1)
        event_types = [r["event_type"] for r in self.audit_log.read_all("INT-3")]
        self.assertIn("evidence_retrieval", event_types)


if __name__ == "__main__":
    unittest.main()
