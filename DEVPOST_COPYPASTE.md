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

The Track 02 prototype is grounded in empirical medical data through an adapter for the public **UCI Heart Disease** dataset. UCI identifies the dataset as a health-and-medicine classification dataset and licenses it under **CC BY 4.0**; the processed Cleveland subset contains 303 instances and UCI notes that names and Social Security numbers were removed/replaced with dummy values. The repository contains the adapter and documentation rather than a vendored raw dataset. Source: https://archive.ics.uci.edu/dataset/45/heart+disease ; DOI: 10.24432/C52P4X.

The implementation includes the pipeline, schema, tests, browser demo, empirical-data adapter, and an offline structural evaluation harness. The software test suite contains 59 tests, and the offline structural evaluation passes.

This is a research/contest prototype, not a medical device or clinical diagnostic tool. The included safety thresholds, evidence configuration, and diagnostic reasoning require clinical validation and independent evaluation before any real-patient use. The project was not deployed on real patients or real clinical decisions.

## Built With
- Python 3
- Python standard library
- JSON Schema
- OpenAI-compatible structured LLM interface (optional interactive path)
- PubMed evidence retrieval interface (optional runtime path)
- UCI Machine Learning Repository — Heart Disease dataset (CC BY 4.0)
- GitHub
- ChatGPT for development assistance

## AI assistance disclosure
ChatGPT was used during development for architecture discussion, code generation/refinement, debugging, documentation, testing support, and submission preparation. The author reviewed the submitted repository and is responsible for the final implementation and claims.

## Repository
https://github.com/Lealom000/diagnostic-ai

## Demo video
[PASTE YOUR PUBLIC YOUTUBE / VIMEO / YOUKU URL HERE]

## Team
Lealom Gebreyes

## Notes for submission
- Use synthetic/demo cases only in the video and screenshots.
- Do not claim clinical validation or real-patient deployment.
- The repository is public and unrestricted.
- Keep the demo video public or unlisted, not private.
