"""LLM-driven differential reasoning component with an explicit output boundary."""
from __future__ import annotations
import json

REASONING_AGENT_TOOL_NAME="submit_differential"
REASONING_AGENT_SCHEMA={"type":"object","required":["hypotheses","missing_information","uncertainty_notes","needs_more_information"],"properties":{"hypotheses":{"type":"array","items":{"type":"object","required":["id","diagnosis","supporting_findings","contradicting_findings","danger_level","current_confidence"],"properties":{"id":{"type":"string"},"diagnosis":{"type":"string"},"supporting_findings":{"type":"array","items":{"type":"string"}},"contradicting_findings":{"type":"array","items":{"type":"string"}},"missing_information":{"type":"array","items":{"type":"string"}},"danger_level":{"type":"string","enum":["low","moderate","high","cannot_exclude_dangerous"]},"current_confidence":{"type":"string","enum":["possible","likely","less_likely"]},"reasons_for_uncertainty":{"type":"array","items":{"type":"string"}},"self_challenge":{"type":"object","properties":{"evidence_against":{"type":"string"},"better_alternative":{"type":"string"},"dangerous_diagnosis_missed":{"type":"string"}},"additionalProperties":False}},"additionalProperties":False}},"missing_information":{"type":"array","items":{"type":"object","required":["variable","tier","rationale"],"properties":{"variable":{"type":"string"},"tier":{"type":"integer","minimum":0,"maximum":5},"rationale":{"type":"string"},"eliminates_dangerous_diagnosis":{"type":"boolean"},"resolves_contradiction":{"type":"boolean"},"discriminating_power":{"type":"string","enum":["low","medium","high"]},"cost_risk":{"type":"string","enum":["low","medium","high"]}},"additionalProperties":False}},"uncertainty_notes":{"type":"array","items":{"type":"string"}},"needs_more_information":{"type":"boolean"}},"additionalProperties":False}
REASONING_AGENT_SYSTEM_PROMPT="""Produce a differential for human review, never a confirmed diagnosis. Use only supplied findings; include dangerous alternatives; self-challenge each hypothesis; identify missing information. Emergency status belongs to the safety gate, not this component."""
_ALLOWED_OUTPUT_KEYS={"hypotheses","missing_information","uncertainty_notes","needs_more_information"}

def _format_patient_state_for_prompt(patient_state:dict)->str:
    relevant={"demographics":patient_state.get("demographics",{}),"entities":patient_state.get("entities",{}),"observed_facts":patient_state.get("observed_facts",[]),"derived_observations":patient_state.get("derived_observations",[]),"existing_hypotheses":patient_state.get("hypotheses",[]),"evidence_gathered_so_far":patient_state.get("evidence",[]),"known_contradictions":patient_state.get("contradictions",[])}
    return json.dumps(relevant,indent=2,default=str)

def _enforce_output_boundary(raw:dict)->dict:
    return {k:v for k,v in raw.items() if k in _ALLOWED_OUTPUT_KEYS}

class LLMReasoningAgent:
    def __init__(self,client): self._client=client
    def generate_hypotheses(self,patient_state:dict)->dict:
        raw=self._client.complete_structured(system=REASONING_AGENT_SYSTEM_PROMPT,user=_format_patient_state_for_prompt(patient_state),tool_name=REASONING_AGENT_TOOL_NAME,tool_description="Submit the differential diagnosis analysis for this case.",input_schema=REASONING_AGENT_SCHEMA)
        return _enforce_output_boundary(raw)
