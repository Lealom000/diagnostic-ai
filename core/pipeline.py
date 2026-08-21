"""End-to-end diagnostic-support research pipeline."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime,timezone
from .audit_log import AuditLog
from .evidence_tool import EvidenceTool
from .next_step_selector import rank_next_steps
from .output_state_machine import CaseSignals,next_review_state
from .patient_state import validate_patient_state
from .safety_gate import SafetyState,run_deterministic_safety_gate,combine_with_llm_pass
from .controller import Decision,ToolCall,check as controller_check

@dataclass
class DiagnosticPipeline:
    reasoning_agent:object
    evidence_tool:EvidenceTool
    llm_safety_pass:object
    audit_log:AuditLog
    def run(self,patient_state:dict)->dict:
        errors=validate_patient_state(patient_state)
        if errors: raise ValueError("Invalid PatientState: "+"; ".join(errors))
        case_id=patient_state["case_id"]
        deterministic=run_deterministic_safety_gate(patient_state)
        llm_flag,llm_reason=self.llm_safety_pass.check(patient_state)
        safety=combine_with_llm_pass(deterministic,llm_flag,llm_reason)
        patient_state["safety_state"]=safety.safety_state.value
        self.audit_log.record(case_id,patient_state["state_version"],"safety_initial",{"state":safety.safety_state.value,"rationale":safety.rationale})
        if safety.safety_state!=SafetyState.NORMAL:
            patient_state["review_state"]="EMERGENCY" if safety.safety_state==SafetyState.EMERGENCY else "HUMAN_REVIEW"
            return patient_state
        reasoning=self.reasoning_agent.generate_hypotheses(patient_state)
        patient_state["hypotheses"]=reasoning.get("hypotheses",[])
        patient_state["missing_information"]=reasoning.get("missing_information",[])
        patient_state["uncertainty_notes"]=reasoning.get("uncertainty_notes",[])
        patient_state["state_version"]+=1; patient_state["updated_at"]=datetime.now(timezone.utc).isoformat()
        self.audit_log.record(case_id,patient_state["state_version"],"reasoning",{"hypothesis_count":len(patient_state["hypotheses"])})
        all_evidence=[]
        for h in patient_state["hypotheses"][:5]:
            claim=h.get("diagnosis","")
            if claim and controller_check(ToolCall("evidence_search",False)).decision==Decision.ALLOW:
                all_evidence.extend(self.evidence_tool.retrieve(claim,h.get("id","")))
        patient_state["evidence"]=all_evidence
        patient_state["recommended_actions"]=rank_next_steps(patient_state["missing_information"])
        deterministic2=run_deterministic_safety_gate(patient_state)
        if deterministic2.safety_state==SafetyState.EMERGENCY:
            patient_state["safety_state"]="EMERGENCY"; patient_state["review_state"]="EMERGENCY"; return patient_state
        dangerous=any(h.get("danger_level")=="cannot_exclude_dangerous" for h in patient_state["hypotheses"])
        missing_change=bool(reasoning.get("needs_more_information")) or bool(patient_state["missing_information"])
        evidence_conflict=any(e.get("claim_supported")=="inconclusive" for e in all_evidence)
        review=next_review_state(CaseSignals(False,bool(patient_state.get("contradictions")),dangerous,evidence_conflict,False,False,missing_change,len(patient_state["hypotheses"])>0))
        patient_state["review_state"]=review.value
        patient_state["state_version"]+=1; patient_state["updated_at"]=datetime.now(timezone.utc).isoformat()
        self.audit_log.record(case_id,patient_state["state_version"],"completed",{"review_state":review.value,"evidence_count":len(all_evidence)})
        return patient_state
