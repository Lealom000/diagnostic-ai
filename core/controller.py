"""
Controller — Section 19/20 of diagnostic-ai-blueprint-v6.md.

Default-deny permission layer. Tool calls are checked against an
explicit, code-level allow-list — never a prompt-based restriction an
LLM could talk itself out of.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Decision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"


@dataclass(frozen=True)
class ToolCall:
    tool_name: str
    is_write: bool


@dataclass
class ControllerResult:
    decision: Decision
    reason: str


READ_ONLY_ALLOW_LIST = {
    "calculator",
    "evidence_search",
    "database_read",
    "clinical_score_calculator",
}

WRITE_ALLOW_LIST = {
    "audit_log_write",
}

DENY_LIST = {
    "medical_order",
    "prescription",
    "patient_record_modify",
    "autonomous_treatment",
}


def check(tool_call: ToolCall) -> ControllerResult:
    if tool_call.tool_name in DENY_LIST:
        return ControllerResult(
            Decision.DENY, f"'{tool_call.tool_name}' is explicitly prohibited (Section 19)."
        )

    if tool_call.is_write:
        if tool_call.tool_name in WRITE_ALLOW_LIST:
            return ControllerResult(
                Decision.ALLOW, f"'{tool_call.tool_name}' is an allow-listed non-clinical write."
            )
        return ControllerResult(
            Decision.DENY,
            f"'{tool_call.tool_name}' is a write-capable call and is not on the "
            "write allow-list — default-deny (Section 19).",
        )

    if tool_call.tool_name in READ_ONLY_ALLOW_LIST:
        return ControllerResult(
            Decision.ALLOW, f"'{tool_call.tool_name}' is an allow-listed read-only tool."
        )

    return ControllerResult(
        Decision.DENY,
        f"'{tool_call.tool_name}' is not on any allow-list — default-deny (Section 19).",
    )
