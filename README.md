# Diagnostic AI
## Safety-Gated LLM Diagnostic-Support Research Prototype

Diagnostic AI is a research/contest prototype for structured, evidence-grounded clinical reasoning with explicit safety boundaries. It is **not a clinically validated medical device**.

### Core idea
The system separates responsibilities instead of giving one LLM unrestricted control:

`PatientState → deterministic safety gate → LLM safety pass + structured reasoning → evidence → next-step ranking → controlled output → audit log`

The reasoning model produces a **differential for human review**, not a confirmed diagnosis. Deterministic components handle exact checks and permissions; the LLM cannot write observations, safety state, emergency status, or completed medical actions.

### Included
- Formal PatientState schema and validator
- Deterministic Tier-0 safety rules
- Independent LLM safety pass
- Structured LLM differential reasoning
- Self-challenge fields
- Evidence retrieval and trust filtering
- Prompt-injection flagging
- Deterministic next-step ranking
- Suggest-only output boundary
- Default-deny controller
- Review-state machine
- Append-only audit logging
- Browser demo
- Offline structural evaluation
- 59 unit tests

### Validation status
The included tests validate software invariants and pipeline behavior. They do **not** establish clinical accuracy. The current prototype has no claim of real-patient deployment or clinical validation.

### Run tests
```bash
python3 -m unittest discover -s tests -t . -v
```

Expected result: `Ran 59 tests ... OK`.

### Run offline evaluation
```bash
python3 evaluate.py
```

Expected result contains:
```json
{"status": "PASS"}
```

### Run the demo
The core pipeline can run with the standard library. For the interactive LLM path, configure the provider variables in `.env.example` and use a compatible structured-LLM backend.

```bash
python3 app.py
```

Then open `http://localhost:8000`.

### Safety / medical-use notice
This project is for research and contest evaluation. It must not be used as a substitute for professional medical care, diagnosis, treatment, or emergency services. Do not deploy it on real patients without appropriate clinical validation, oversight, security review, and regulatory assessment.

See `SUBMISSION.md`, `BLUEPRINT.md`, and `docs/Diagnostic_AI_Contest_Submission.pdf` for the fuller specification and submission material.
