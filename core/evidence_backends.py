"""Evidence search backends.

The default online backend uses PubMed's public E-utilities API. No LLM is
involved in retrieval: the LLM only assesses already-retrieved text.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass


@dataclass
class PubMedBackend:
    email: str = ""
    retmax: int = 3
    timeout: int = 20

    def search(self, query: str) -> list[dict]:
        params = {"db": "pubmed", "term": query, "retmode": "json", "retmax": str(self.retmax)}
        if self.email:
            params["email"] = self.email
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + urllib.parse.urlencode(params)
        with urllib.request.urlopen(url, timeout=self.timeout) as r:
            ids = json.loads(r.read().decode()).get("esearchresult", {}).get("idlist", [])
        if not ids:
            return []
        summary_params = {"db": "pubmed", "id": ",".join(ids), "retmode": "json"}
        if self.email:
            summary_params["email"] = self.email
        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + urllib.parse.urlencode(summary_params)
        with urllib.request.urlopen(summary_url, timeout=self.timeout) as r:
            result = json.loads(r.read().decode()).get("result", {})
        items = []
        for pmid in ids:
            row = result.get(pmid, {})
            title = row.get("title", "")
            items.append({
                "source": "PubMed",
                "title": title,
                "date": row.get("pubdate", ""),
                "domain": "pubmed.ncbi.nlm.nih.gov",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "snippet": title,
            })
        return items


@dataclass
class StaticEvidenceBackend:
    results: list[dict]

    def search(self, query: str) -> list[dict]:
        return list(self.results)
