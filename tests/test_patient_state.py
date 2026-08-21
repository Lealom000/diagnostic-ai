import unittest

from core.patient_state import new_patient_state, validate_patient_state


def _minimal_valid_state():
    return new_patient_state(case_id="SYN-0001", created_at="2026-08-21T00:00:00Z", audit_ref="AUD-0001")


class TestPatientStateValidation(unittest.TestCase):
    def test_minimal_state_is_valid(self):
        self.assertEqual(validate_patient_state(_minimal_valid_state()), [])

    def test_missing_required_field_rejected(self):
        state = _minimal_valid_state(); del state["safety_state"]
        self.assertTrue(any("safety_state" in e for e in validate_patient_state(state)))

    def test_invalid_safety_state_value_rejected(self):
        state = _minimal_valid_state(); state["safety_state"] = "PROBABLY_FINE"
        self.assertTrue(any("safety_state" in e for e in validate_patient_state(state)))

    def test_recommended_action_status_locked_to_recommended_only(self):
        state = _minimal_valid_state()
        state["recommended_actions"] = [{"action": "order ECG", "rationale": "chest pain", "status": "ordered"}]
        self.assertTrue(any("recommended_only" in e for e in validate_patient_state(state)))

    def test_observed_fact_cannot_claim_derived_status(self):
        state = _minimal_valid_state()
        state["observed_facts"] = [{"id": "F1", "variable": "temperature", "value": 39.1, "source": "patient_device", "timestamp": "2026-08-21T00:00:00Z", "confidence": "high", "status": "derived_interpretation"}]
        self.assertTrue(any("observed_facts[0].status" in e for e in validate_patient_state(state)))

    def test_valid_recommended_action_passes(self):
        state = _minimal_valid_state()
        state["recommended_actions"] = [{"action": "consider oxygen saturation check", "rationale": "respiratory complaint", "status": "recommended_only"}]
        self.assertEqual(validate_patient_state(state), [])


if __name__ == "__main__":
    unittest.main()
