"""Patient State validation and constructor."""
from __future__ import annotations

REQUIRED_TOP_LEVEL=["case_id","created_at","updated_at","state_version","observed_facts","derived_observations","hypotheses","evidence","missing_information","contradictions","uncertainty_notes","recommended_actions","safety_state","review_state","audit_ref"]
SAFETY_STATES={"NORMAL","EMERGENCY","HUMAN_REVIEW"}
REVIEW_STATES={"INFO_ONLY","MORE_INFORMATION_NEEDED","DIFFERENTIAL","HUMAN_REVIEW","EMERGENCY","ABSTAIN"}

def validate_patient_state(state:dict)->list[str]:
    errors=[]
    for field in REQUIRED_TOP_LEVEL:
        if field not in state: errors.append(f"missing required field: '{field}'")
    if "state_version" in state and not(isinstance(state["state_version"],int) and state["state_version"]>=1): errors.append("'state_version' must be an integer >= 1")
    if "safety_state" in state and state["safety_state"] not in SAFETY_STATES: errors.append(f"'safety_state' must be one of {sorted(SAFETY_STATES)}")
    if "review_state" in state and state["review_state"] not in REVIEW_STATES: errors.append(f"'review_state' must be one of {sorted(REVIEW_STATES)}")
    for i,fact in enumerate(state.get("observed_facts",[])):
        if fact.get("status")!="observed": errors.append(f"observed_facts[{i}].status must be 'observed'")
    for i,obs in enumerate(state.get("derived_observations",[])):
        if obs.get("status")!="derived_interpretation": errors.append(f"derived_observations[{i}].status must be 'derived_interpretation'")
    for i,action in enumerate(state.get("recommended_actions",[])):
        if action.get("status")!="recommended_only": errors.append(f"recommended_actions[{i}].status must be 'recommended_only'")
    return errors

def new_patient_state(case_id:str,created_at:str,audit_ref:str)->dict:
    return {"case_id":case_id,"created_at":created_at,"updated_at":created_at,"state_version":1,"demographics":{},"entities":{},"observed_facts":[],"derived_observations":[],"hypotheses":[],"evidence":[],"missing_information":[],"contradictions":[],"uncertainty_notes":[],"recommended_actions":[],"safety_state":"NORMAL","review_state":"INFO_ONLY","audit_ref":audit_ref}
