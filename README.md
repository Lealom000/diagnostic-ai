# Diagnostic AI
## Safety-Gated LLM Diagnostic-Support Research Prototype

Diagnostic AI is a research/contest prototype for structured, evidence-grounded clinical reasoning with explicit safety boundaries. It is **not a medical device, not a clinical diagnostic tool, and not a substitute for professional medical care**.

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
- Empirical-data adapter for the public UCI Heart Disease dataset

### Empirical dataset and data ethics
The Track 02 prototype uses the **UCI Heart Disease** dataset as an empirical, real-world validation source for structured patient-state mapping and offline pipeline evaluation. UCI describes the processed Cleveland subset as 303 instances with 13 features and notes that names and Social Security numbers were removed/replaced with dummy values. The dataset is licensed **CC BY 4.0**.

Source: UCI Machine Learning Repository, *Heart Disease*, DOI `10.24432/C52P4X`.

Dataset page: https://archive.ics.uci.edu/dataset/45/heart+disease

The repository does not contain a vendored raw copy. Run `python data/prepare_uci_heart.py` to retrieve the public archive and create a local snapshot for offline work. Do not use identifiable patient records or personal health records.

### Validation status
The included tests validate software invariants and pipeline behavior. They do **not** establish clinical accuracy. The empirical dataset adapter validates data handling and schema compatibility; it is not a claim that this prototype has been clinically validated.

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

### Prepare the empirical dataset locally
```bash
python3 data/prepare_uci_heart.py
```

### Run the demo
The core pipeline can run with the standard library. For the interactive LLM path, configure the provider variables in `.env.example` and use a compatible structured-LLM backend.

```bash
python3 app.py
```

Then open `http://localhost:8000`.

### AI assistance disclosure
AI coding assistants were used during development. **ChatGPT** was used for architecture discussion, code generation/refinement, debugging, documentation, testing support, and submission preparation. The submitted repository was reviewed by the author, who is responsible for the final implementation and must be able to explain its operation.

### Built With
- Python 3
- Python standard library
- Structured LLM tool-calling / OpenAI-compatible API interface (optional interactive path)
- UCI Machine Learning Repository — Heart Disease dataset (CC BY 4.0)
- GitHub
- ChatGPT (development assistance)

### Safety / medical-use notice
This project is for research and contest evaluation. It must not be used as a substitute for professional medical care, diagnosis, treatment, or emergency services. Do not deploy it on real patients or real clinical decisions without appropriate clinical validation, oversight, security review, and regulatory assessment.

See `SUBMISSION.md`, `BLUEPRINT.md`, and `docs/Diagnostic_AI_Contest_Submission.pdf` for the fuller specification and submission material.
