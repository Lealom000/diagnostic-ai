#!/usr/bin/env python3
"""Browser demo for the Diagnostic AI research prototype."""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

from core.audit_log import AuditLog
from core.evidence_tool import EvidenceTool
from core.llm_client import OpenAICompatibleLLMClient, ScriptedLLMClient
from core.llm_safety_pass import LLMSafetyPass
from core.patient_state import new_patient_state
from core.pipeline import DiagnosticPipeline
from core.reasoning_agent import LLMReasoningAgent

HTML = '''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Diagnostic AI Research Prototype</title><style>body{font-family:system-ui;max-width:1100px;margin:32px auto;padding:0 20px;background:#0d1117;color:#eef2f7}h1{margin-bottom:8px}.warning{background:#3a3214;border:1px solid #6b5a22;padding:12px;border-radius:10px;margin-bottom:18px}.panel{background:#151b23;border:1px solid #303b49;border-radius:12px;padding:16px;margin-bottom:16px}textarea{width:100%%;min-height:230px;resize:vertical;background:#0b1016;color:#eef2f7;border:1px solid #303b49;border-radius:10px;padding:12px;font:13px/1.5 ui-monospace,monospace}button{padding:12px 18px;margin-top:12px;border:0;border-radius:10px;background:#6ea8fe;color:#081018;font-weight:700;cursor:pointer}.tag{display:inline-block;border:1px solid #45d483;color:#45d483;padding:5px 9px;border-radius:999px;font-size:12px;margin-right:8px}pre{white-space:pre-wrap;background:#0b1016;border:1px solid #303b49;padding:18px;border-radius:10px;overflow:auto}</style></head><body><h1>Diagnostic AI — Research Prototype</h1><div class="warning">Research/contest prototype only. Not a medical device. It does not provide confirmed diagnoses, prescriptions, or medical orders.</div><div class="panel"><span class="tag">Safety-gated</span><span class="tag">Evidence-grounded</span><span class="tag">Human review</span>%s</div><form method="post"><div class="panel"><h3>Case JSON</h3><textarea name="case">%s</textarea><br><button>Run diagnostic pipeline</button></div></form>%s</body></html>'''

DEFAULT = json.dumps({
    "demographics": {"age_band": "adult", "sex": "unknown"},
    "observed_facts": [
        {"id": "f1", "variable": "chief_complaint", "value": "persistent cough and fever for 3 days", "source": "synthetic_demo", "timestamp": "2026-08-21T00:00:00Z", "confidence": "high", "status": "observed"},
        {"id": "f2", "variable": "oxygen_saturation", "value": 98, "unit": "%", "source": "synthetic_demo", "timestamp": "2026-08-21T00:00:00Z", "confidence": "high", "status": "observed"},
        {"id": "f3", "variable": "temperature", "value": 38.2, "unit": "C", "source": "synthetic_demo", "timestamp": "2026-08-21T00:00:00Z", "confidence": "high", "status": "observed"}
    ],
    "entities": {}
}, indent=2)

class OfflineBackend:
    def search(self, query: str) -> list[dict]:
        return [{
            "domain": "pubmed.ncbi.nlm.nih.gov",
            "source": "PubMed",
            "title": f"Structured evidence for: {query}",
            "date": "2026",
            "snippet": f"Reference summary supporting evaluation of the claim: {query}.",
            "url": "https://pubmed.ncbi.nlm.nih.gov/"
        }]


def build_pipeline() -> tuple[DiagnosticPipeline, str]:
    mode = os.getenv("DIAG_DEMO_MODE", "live").lower()
    audit_path = "runtime/audit.jsonl"
    if mode == "offline":
        llm = ScriptedLLMClient(responses=[
            {"emergency_pattern_detected": False, "rationale": "No Tier-0 emergency pattern detected in this synthetic demonstration."},
            {"hypotheses": [
                {"id":"H1","diagnosis":"Community-acquired pneumonia","supporting_findings":["cough","fever"],"contradicting_findings":[],"danger_level":"moderate","current_confidence":"possible"},
                {"id":"H2","diagnosis":"Viral respiratory infection","supporting_findings":["cough","fever"],"contradicting_findings":[],"danger_level":"low","current_confidence":"likely"},
                {"id":"H3","diagnosis":"Pulmonary embolism","supporting_findings":[],"contradicting_findings":[],"danger_level":"cannot_exclude_dangerous","current_confidence":"less likely"}
            ],"missing_information":[{"variable":"respiratory_rate","tier":0,"rationale":"Severity assessment","priority":"high"},{"variable":"chest_examination","tier":2,"rationale":"Could change the differential","priority":"high"}],"uncertainty_notes":["Synthetic offline demonstration"],"needs_more_information":True},
            {"claim_supported":"partial","retrieved_text_summary":"Evidence is consistent with the evaluated claim in this synthetic/offline demonstration."},
            {"claim_supported":"partial","retrieved_text_summary":"Evidence is consistent with the evaluated claim in this synthetic/offline demonstration."},
            {"claim_supported":"inconclusive","retrieved_text_summary":"Evidence is intentionally inconclusive for the dangerous alternative and is not a clinical conclusion."},
        ])
        llm_safety = LLMSafetyPass(llm)
        reasoning = LLMReasoningAgent(llm)
        evidence = EvidenceTool(OfflineBackend(), llm)
        return DiagnosticPipeline(reasoning, evidence, llm_safety, AuditLog(audit_path)), "offline"
    llm = OpenAICompatibleLLMClient()
    return DiagnosticPipeline(LLMReasoningAgent(llm), EvidenceTool(__import__('core.evidence_backends', fromlist=['PubMedBackend']).PubMedBackend(), llm), LLMSafetyPass(llm), AuditLog(audit_path)), "live"


class Handler(BaseHTTPRequestHandler):
    def _page(self, case=DEFAULT, result="", mode="live"):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        badge = '<span style="color:#45d483">OFFLINE DEMO MODE — scripted, no API key required</span>' if mode == "offline" else '<span>LIVE LLM MODE</span>'
        self.wfile.write((HTML % (badge, case.replace("&", "&amp;").replace("<", "&lt;"), result)).encode())

    def do_GET(self):
        _, mode = build_pipeline()
        self._page(mode=mode)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(n).decode()
        data = parse_qs(raw)
        text = data.get("case", [DEFAULT])[0]
        try:
            user = json.loads(text)
            case = new_patient_state("case-" + uuid.uuid4().hex[:10], datetime.now(timezone.utc).isoformat(), "audit")
            for key, value in user.items():
                if key in case:
                    case[key] = value
            pipeline, mode = build_pipeline()
            result = pipeline.run(case)
            self._page(text, "<div class=\"panel\"><h2>Pipeline Result</h2><pre>" + json.dumps(result, indent=2).replace("<", "&lt;") + "</pre></div>", mode=mode)
        except Exception as exc:
            self._page(text, "<div class=\"panel\"><h2>Error</h2><pre>" + str(exc).replace("<", "&lt;") + "</pre></div>", mode=os.getenv("DIAG_DEMO_MODE", "live"))


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"Open http://localhost:{port}")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


def main():
    port = int(os.getenv("PORT", "8000"))
    print(f"Open http://localhost:{port}")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
