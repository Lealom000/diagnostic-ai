"""
Audit Log — Section 26 of diagnostic-ai-blueprint-v6.md.

Append-only, one record per state transition. For the prototype, a
local JSONL file is sufficient as long as nothing in the pipeline is
ever given delete/modify access to it — enforced by the Controller
(Section 19): 'audit_log_write' is allow-listed for append only, and
there is no 'audit_log_delete' or 'audit_log_modify' entry anywhere on
any allow-list.
"""

from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class AuditRecord:
    case_id: str
    timestamp: str
    patient_state_version: int
    event_type: str
    detail: dict[str, Any] = field(default_factory=dict)


class AuditLog:
    def __init__(self, path: str):
        self._path = path
        self._lock = threading.Lock()
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)

    def record(
        self,
        case_id: str,
        patient_state_version: int,
        event_type: str,
        detail: Optional[dict] = None,
    ) -> AuditRecord:
        entry = AuditRecord(
            case_id=case_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            patient_state_version=patient_state_version,
            event_type=event_type,
            detail=detail or {},
        )
        with self._lock:
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(entry)) + "\n")
        return entry

    def read_all(self, case_id: Optional[str] = None) -> list[dict]:
        if not os.path.exists(self._path):
            return []
        records = []
        with open(self._path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                if case_id is None or rec["case_id"] == case_id:
                    records.append(rec)
        return records
