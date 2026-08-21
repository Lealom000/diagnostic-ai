# Devpost Submission — Copy/Paste Draft

## Project name
Diagnostic AI

## Tagline
Safety-Gated LLM Diagnostic-Support Research Prototype

## Short description
Diagnostic AI is a research prototype for structured, evidence-grounded clinical reasoning with explicit safety boundaries. It separates observations from hypotheses and recommendations, uses deterministic safety gates around LLM reasoning, and produces a differential for human review rather than a confirmed diagnosis.

## Full description
Diagnostic AI explores whether a structured, evidence-grounded, iterative reasoning architecture can make LLM-assisted medical diagnostic reasoning safer and more auditable than an LLM operating alone.

The prototype uses a formal PatientState schema and separates system responsibilities by authority. Deterministic components handle exact checks and permissions. The reasoning LLM generates a structured differential, identifies missing information, cites supporting and contradicting evidence, and self-challenges the leading hypotheses. A separate safety pass can only agree or escalate disagreement for human review. Retrieved web content is treated as inert data rather than instructions, with domain trust filtering and prompt-injection flagging. A default-deny controller prevents the model from performing actions it is not authorized to perform. Recommended tests or next steps remain suggestions only.

The implementation includes the pipeline, schema, tests, browser demo, and an offline structural evaluation harness. The current test suite contains 59 tests and the offline evaluation runs without network access.

This is a research/contest prototype, not a clinically validated medical device. The included safety thresholds, evidence configuration, and diagnostic reasoning require clinical validation and independent evaluation before any real-patient use.

## Built with
- Python
- JSON Schema
- Structured LLM tool calling
- PubMed evidence retrieval
- Python standard library for the core/test harness

## Repository
[PASTE YOUR PUBLIC GITHUB URL HERE]

## Demo video
[PASTE YOUR YOUTUBE/VIDEO URL HERE]

## Team
Lealom Gebreyes

## Notes for submission
- Use synthetic/demo cases only.
- Do not claim clinical validation or real-patient deployment.
- Replace the repository and video placeholders before submitting.
