"""LLM safety pass used alongside the deterministic safety gate."""
from __future__ import annotations
import json
from dataclasses import dataclass

SAFETY_PASS_TOOL_NAME = "report_safety_assessment"
SAFETY_PASS_SCHEMA = {
    "type":"object","required":["emergency_pattern_detected","rationale"],
    "properties":{"emergency_pattern_detected":{"type":"boolean"},"rationale":{"type":"string"}},
    "additionalProperties":False,
}
SAFETY_PASS_SYSTEM_PROMPT = """You are the broad safety pass of a research diagnostic-support prototype. Catch dangerous patterns a fixed rule set could miss. Err toward human review when genuinely uncertain. You do not decide final safety status; your result is combined with a deterministic pass."""

@dataclass
class LLMSafetyPass:
    llm: object
    def check(self, patient_state: dict) -> tuple[bool,str]:
        user_prompt=json.dumps({"observed_facts":patient_state.get("observed_facts",[]),"derived_observations":patient_state.get("derived_observations",[])},indent=2,default=str)
        result=self.llm.complete_structured(system=SAFETY_PASS_SYSTEM_PROMPT,user=user_prompt,tool_name=SAFETY_PASS_TOOL_NAME,tool_description="Report whether the case suggests a medical emergency.",input_schema=SAFETY_PASS_SCHEMA)
        return bool(result["emergency_pattern_detected"]), result.get("rationale","")
