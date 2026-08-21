# Diagnostic AI — Contest Submission Package

## Abstract
Diagnostic AI is a safety-gated, LLM-assisted clinical reasoning research prototype. It separates reality from observations, interpretations, hypotheses, recommendations, and retrospective outcomes. A deterministic safety gate runs before and after reasoning; an independent LLM safety pass can only agree with it or escalate disagreement to human review. The reasoning model produces a structured differential rather than a confirmed diagnosis. Evidence retrieval is allow-listed and retrieved content is treated as inert data. A controller enforces default-deny tool permissions, and an append-only audit log records state transitions.

## What is implemented
- Structured PatientState schema and validator
- Deterministic Tier-0 safety rules
- Independent broad LLM safety pass
- Structured LLM differential reasoning
- Self-challenge fields for each hypothesis
- Evidence retrieval through PubMed
- Domain trust filtering and prompt-injection flagging
- Deterministic next-step ranking
- Suggest-only output boundary
- Default-deny controller
- Review-state state machine
- Append-only audit logging
- Browser demo with no frontend framework
- 59 legacy unit tests retained

## Important limitation
This is a research/contest prototype, not a validated clinical device. The included emergency thresholds, evidence allow-list, and diagnostic reasoning have not been clinically validated. No real-patient deployment is claimed.

## Run
1. Set `DIAG_LLM_BASE_URL`, `DIAG_LLM_API_KEY`, and `DIAG_LLM_MODEL`.
2. Run `python3 app.py`.
3. Open `http://localhost:8000`.
4. Paste a synthetic case JSON and run the pipeline.

## Test
`python3 -m unittest discover -s tests -t . -v`
