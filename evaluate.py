"""Offline structural evaluation for the contest package.

This does NOT measure clinical accuracy. It checks safety invariants and
output boundaries using scripted model responses, so it is deterministic and
network-free.
"""
from __future__ import annotations
import json
from core.audit_log import AuditLog
from core.evidence_backends import StaticEvidenceBackend
from core.evidence_tool import EvidenceTool
from core.llm_client import ScriptedLLMClient
from core.llm_safety_pass import LLMSafetyPass
from core.patient_state import new_patient_state
from core.pipeline import DiagnosticPipeline
from core.reasoning_agent import LLMReasoningAgent


def run():
    responses = [
        {"emergency_pattern_detected": False, "rationale": "No urgent pattern in synthetic case."},
        {"hypotheses": [{"id":"H1","diagnosis":"synthetic respiratory syndrome","supporting_findings":["f1"],"contradicting_findings":[],"danger_level":"low","current_confidence":"possible","missing_information":[],"reasons_for_uncertainty":["Synthetic evaluation"],"self_challenge":{"evidence_against":"Other causes remain possible","better_alternative":"Other respiratory cause","dangerous_diagnosis_missed":"Serious respiratory disease"}}],"missing_information":[],"uncertainty_notes":["Synthetic only"],"needs_more_information":False},
        {"claim_supported":"partial","retrieved_text_summary":"Synthetic reference content is not clinical evidence."},
    ]
    client = ScriptedLLMClient(responses)
    state = new_patient_state("eval-001", "2026-01-01T00:00:00+00:00", "audit")
    state["observed_facts"] = [{"id":"f1","variable":"chief_complaint","value":"synthetic cough","source":"synthetic","timestamp":"2026-01-01T00:00:00Z","confidence":"high","status":"observed"}]
    backend = StaticEvidenceBackend([{"source":"PubMed","title":"Synthetic study","date":"2026","domain":"pubmed.ncbi.nlm.nih.gov","url":"https://pubmed.ncbi.nlm.nih.gov/0/","snippet":"Synthetic reference."}])
    pipeline = DiagnosticPipeline(LLMReasoningAgent(client), EvidenceTool(backend, client), LLMSafetyPass(client), AuditLog("/tmp/diagnostic_eval.jsonl"))
    result = pipeline.run(state)
    assert result["review_state"] in {"DIFFERENTIAL", "MORE_INFORMATION_NEEDED", "HUMAN_REVIEW"}
    assert all(a.get("status") == "recommended_only" for a in result["recommended_actions"])
    assert result["safety_state"] == "NORMAL"
    print(json.dumps({"status":"PASS","hypotheses":len(result["hypotheses"]),"evidence":len(result["evidence"]),"review_state":result["review_state"]}, indent=2))

if __name__ == "__main__": run()
