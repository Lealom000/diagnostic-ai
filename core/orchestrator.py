"""Wiring for safety, reasoning, evidence, next-step selection, and audit logging."""
from __future__ import annotations
from dataclasses import dataclass
from .audit_log import AuditLog
from .controller import Decision,ToolCall,check as controller_check
from .next_step_selector import rank_next_steps
from .safety_gate import SafetyState,combine_with_llm_pass,run_deterministic_safety_gate

@dataclass
class Orchestrator:
    audit_log:AuditLog
    reasoning_agent:object
    evidence_tool:object
    llm_safety_pass:object
    def run_safety_check(self,patient_state:dict,case_id:str)->SafetyState:
        deterministic=run_deterministic_safety_gate(patient_state)
        llm_flag,llm_reason=self.llm_safety_pass.check(patient_state)
        combined=combine_with_llm_pass(deterministic,llm_flag,llm_reason)
        self.audit_log.record(case_id,patient_state.get("state_version",0),"safety_check",{"result":combined.safety_state.value,"rationale":combined.rationale})
        return combined.safety_state
    def run_reasoning_step(self,patient_state:dict,case_id:str)->dict:
        result=self.reasoning_agent.generate_hypotheses(patient_state)
        self.audit_log.record(case_id,patient_state.get("state_version",0),"reasoning_step",{"hypothesis_count":len(result.get("hypotheses",[]))})
        return result
    def run_evidence_retrieval(self,claim:str,hypothesis_id:str,case_id:str,patient_state_version:int)->list[dict]:
        results=self.evidence_tool.retrieve(claim,hypothesis_id)
        self.audit_log.record(case_id,patient_state_version,"evidence_retrieval",{"claim":claim,"hypothesis_id":hypothesis_id,"result_count":len(results)})
        return results
    def run_next_step_selection(self,missing_information:list[dict])->list[dict]:
        return rank_next_steps(missing_information)
    def request_tool(self,tool_name:str,is_write:bool)->Decision:
        return controller_check(ToolCall(tool_name=tool_name,is_write=is_write)).decision
