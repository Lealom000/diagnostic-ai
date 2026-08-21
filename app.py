#!/usr/bin/env python3
"""Browser demo for the Diagnostic AI research prototype."""
from __future__ import annotations
import json, os, uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs
from core.audit_log import AuditLog
from core.evidence_backends import PubMedBackend
from core.evidence_tool import EvidenceTool
from core.llm_client import OpenAICompatibleLLMClient
from core.llm_safety_pass import LLMSafetyPass
from core.patient_state import new_patient_state
from core.pipeline import DiagnosticPipeline
from core.reasoning_agent import LLMReasoningAgent

HTML = '''<!doctype html><html><head><meta charset="utf-8"><title>Diagnostic AI Research Prototype</title><style>body{font-family:system-ui;max-width:1000px;margin:40px auto;padding:0 20px}textarea{width:100%%;min-height:180px}button{padding:12px 18px;margin-top:12px}pre{white-space:pre-wrap;background:#f5f5f5;padding:18px;border-radius:8px}.warning{background:#fff3cd;padding:12px;border-radius:8px}</style></head><body><h1>Diagnostic AI — Research Prototype</h1><div class="warning">Research/contest prototype only. Not a medical device. It does not provide confirmed diagnoses, prescriptions, or medical orders.</div><form method="post"><h3>Case JSON</h3><textarea name="case">%s</textarea><br><button>Run diagnostic pipeline</button></form>%s</body></html>'''

DEFAULT = json.dumps({"demographics":{"age_band":"adult","sex":"unknown"},"observed_facts":[{"id":"f1","variable":"chief_complaint","value":"persistent cough and fever","source":"user","timestamp":"now","confidence":"high","status":"observed"}],"entities":{}}, indent=2)

class Handler(BaseHTTPRequestHandler):
    def _page(self, case=DEFAULT, result=""):
        self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.end_headers()
        self.wfile.write((HTML % (case.replace("&","&amp;").replace("<","&lt;"), result)).encode())
    def do_GET(self): self._page()
    def do_POST(self):
        n=int(self.headers.get("Content-Length","0")); raw=self.rfile.read(n).decode(); data=parse_qs(raw); text=data.get("case",[DEFAULT])[0]
        try:
            user=json.loads(text)
            case=new_patient_state("case-"+uuid.uuid4().hex[:10], datetime.now(timezone.utc).isoformat(), "audit")
            for k,v in user.items():
                if k in case: case[k]=v
            llm=OpenAICompatibleLLMClient()
            pipeline=DiagnosticPipeline(LLMReasoningAgent(llm), EvidenceTool(PubMedBackend(), llm), LLMSafetyPass(llm), AuditLog("runtime/audit.jsonl"))
            result=pipeline.run(case)
            self._page(text, "<h2>Result</h2><pre>"+json.dumps(result,indent=2).replace("<","&lt;")+"</pre>")
        except Exception as e:
            self._page(text, "<h2>Error</h2><pre>"+str(e).replace("<","&lt;")+"</pre>")

if __name__ == "__main__":
    port=int(os.getenv("PORT","8000")); print(f"Open http://localhost:{port}"); ThreadingHTTPServer(("0.0.0.0",port),Handler).serve_forever()

def main():
    port=int(os.getenv("PORT","8000")); print(f"Open http://localhost:{port}"); ThreadingHTTPServer(("0.0.0.0",port),Handler).serve_forever()
