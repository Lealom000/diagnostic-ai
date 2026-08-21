"""Output review-state machine. There is no confirmed-diagnosis terminal state."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class ReviewState(str,Enum):
    INFO_ONLY="INFO_ONLY"; MORE_INFORMATION_NEEDED="MORE_INFORMATION_NEEDED"; DIFFERENTIAL="DIFFERENTIAL"; HUMAN_REVIEW="HUMAN_REVIEW"; EMERGENCY="EMERGENCY"; ABSTAIN="ABSTAIN"

@dataclass
class CaseSignals:
    tier0_emergency: bool
    unresolved_important_contradiction: bool
    dangerous_diagnosis_not_excludable: bool
    evidence_conflict_unresolved: bool
    required_tool_unavailable: bool
    case_outside_scope: bool
    missing_info_would_change_ranking: bool
    has_sufficient_differential: bool

def next_review_state(signals:CaseSignals)->ReviewState:
    if signals.tier0_emergency:return ReviewState.EMERGENCY
    if signals.unresolved_important_contradiction:return ReviewState.HUMAN_REVIEW
    if signals.dangerous_diagnosis_not_excludable:return ReviewState.HUMAN_REVIEW
    if signals.evidence_conflict_unresolved or signals.required_tool_unavailable or signals.case_outside_scope:return ReviewState.ABSTAIN
    if signals.missing_info_would_change_ranking:return ReviewState.MORE_INFORMATION_NEEDED
    if signals.has_sufficient_differential:return ReviewState.DIFFERENTIAL
    return ReviewState.INFO_ONLY
