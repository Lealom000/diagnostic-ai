# Empirical dataset used for Track 02 validation

## UCI Heart Disease

This prototype includes an adapter for the **UCI Heart Disease** dataset so the PatientState representation and diagnostic-pipeline validation are grounded in empirical clinical data rather than only synthetic cases.

**Source:** UCI Machine Learning Repository, Heart Disease dataset, DOI `10.24432/C52P4X`.

**License:** Creative Commons Attribution 4.0 International (CC BY 4.0).

**Data characteristics:** UCI documents the dataset as a health-and-medicine classification dataset. The processed Cleveland subset contains 303 instances and 13 features; UCI notes that names and Social Security numbers were removed/replaced with dummy values.

Source page: https://archive.ics.uci.edu/dataset/45/heart+disease

Citation:
Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1989). Heart Disease [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C52P4X

## Use in this project

The dataset is used offline to validate that empirical patient records can be mapped into the project's structured `PatientState` representation and carried through the safety/reasoning/evaluation boundary without introducing identifiable patient information. It is **not** used as evidence for a clinical-accuracy claim, and the prototype is not deployed on real patients or real clinical decisions.

The raw dataset is intentionally not vendored into the repository. `prepare_uci_heart.py` retrieves the public dataset when a user explicitly runs the preparation step.
