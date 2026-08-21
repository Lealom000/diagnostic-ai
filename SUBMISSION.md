# Diagnostic AI — Contest Submission Package

## Abstract
Diagnostic AI is a safety-gated, LLM-assisted clinical reasoning research prototype. It separates reality from observations, interpretations, hypotheses, recommendations, and retrospective outcomes. A deterministic safety gate runs before and after reasoning; an independent LLM safety pass can only agree with it or escalate disagreement to human review. The reasoning model produces a structured differential rather than a confirmed diagnosis. Evidence retrieval is allow-listed and retrieved content is treated as inert data. A controller enforces default-deny tool permissions, and an append-only audit log records state transitions.

## Track 02 empirical-data grounding
The Track 02 implementation is grounded in empirical clinical data using the public **UCI Heart Disease** dataset. UCI lists it as a Health and Medicine classification dataset and reports that the processed Cleveland subset has 303 instances and 13 features. UCI also notes that names and Social Security numbers were removed/replaced with dummy values. The dataset is licensed **CC BY 4.0**.

Source: https://archive.ics.uci.edu/dataset/45/heart+disease
DOI: `10.24432/C52P4X`

The repository includes `data/prepare_uci_heart.py` and `data/evaluate_uci_adapter.py` for explicit offline retrieval and schema-mapping validation. The raw dataset is not vendored into the repository.

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
- Offline demo mode using the actual `DiagnosticPipeline`
- Empirical-data adapter
- 59 unit tests retained

## AI assistance disclosure
ChatGPT was used during development for architecture discussion, code generation/refinement, debugging, documentation, testing support, and submission preparation. The author reviewed the repository and is responsible for the final implementation and claims.

## Important limitation
This is a research/contest prototype, not a medical device or clinical diagnostic tool. The included emergency thresholds, evidence allow-list, and diagnostic reasoning have not been clinically validated. No real-patient deployment or real clinical decision use is claimed.

## Run live mode
1. Set `DIAG_LLM_BASE_URL`, `DIAG_LLM_API_KEY`, and `DIAG_LLM_MODEL`.
2. Run `python3 app.py`.
3. Open `http://localhost:8000`.
4. Paste a synthetic case JSON and run the pipeline.

## Run offline demo mode (no API key)
1. Set `DIAG_DEMO_MODE=offline`.
2. Run `python3 app.py`.
3. Open `http://localhost:8000`.
4. Use the synthetic case already shown in the browser and run the pipeline.

The offline mode uses the real safety gate, reasoning agent, evidence tool, next-step selector, output state machine, and audit log with scripted model responses. It is for demonstration/testing only and must not be described as a live clinical inference.

## Test
`python3 -m unittest discover -s tests -t . -v`
