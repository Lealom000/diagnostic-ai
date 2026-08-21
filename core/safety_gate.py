"""Deterministic first-pass safety gate and disagreement handling."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Callable

class SafetyState(str,Enum):
    NORMAL="NORMAL"; EMERGENCY="EMERGENCY"; HUMAN_REVIEW="HUMAN_REVIEW"

@dataclass(frozen=True)
class SafetyRule:
    rule_id:str; description:str; predicate:Callable[[dict],bool]

@dataclass
class SafetyGateResult:
    safety_state:SafetyState; triggered_rule_ids:list[str]; rationale:str

def _has_observed(patient_state:dict,variable:str,predicate:Callable)->bool:
    return any(f.get("variable")==variable and predicate(f.get("value")) for f in patient_state.get("observed_facts",[]))

RULES=[
 SafetyRule("R-SPO2-CRIT","Oxygen saturation below 90%",lambda ps:_has_observed(ps,"oxygen_saturation",lambda v:isinstance(v,(int,float)) and v<90)),
 SafetyRule("R-CONSCIOUSNESS-ALTERED","Severely altered consciousness reported",lambda ps:_has_observed(ps,"consciousness",lambda v:str(v).lower() in {"unresponsive","severely_altered"})),
 SafetyRule("R-BLEEDING-MAJOR","Major bleeding reported",lambda ps:_has_observed(ps,"bleeding_severity",lambda v:str(v).lower()=="major")),
]

def run_deterministic_safety_gate(patient_state:dict)->SafetyGateResult:
    triggered=[r.rule_id for r in RULES if r.predicate(patient_state)]
    if triggered:return SafetyGateResult(SafetyState.EMERGENCY,triggered,f"Deterministic Tier-0 rule(s) triggered: {', '.join(triggered)}")
    return SafetyGateResult(SafetyState.NORMAL,[],"No deterministic Tier-0 rules triggered.")

def combine_with_llm_pass(deterministic:SafetyGateResult,llm_flagged_emergency:bool,llm_rationale:str="")->SafetyGateResult:
    det_flagged=deterministic.safety_state==SafetyState.EMERGENCY
    if det_flagged and llm_flagged_emergency:return deterministic
    if not det_flagged and not llm_flagged_emergency:return deterministic
    return SafetyGateResult(SafetyState.HUMAN_REVIEW,deterministic.triggered_rule_ids,f"Deterministic and LLM safety passes disagreed (deterministic={deterministic.safety_state.value}, llm_flagged_emergency={llm_flagged_emergency}: '{llm_rationale}'). Escalated to HUMAN_REVIEW.")
