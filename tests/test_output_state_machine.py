import unittest

from core.output_state_machine import CaseSignals, ReviewState, next_review_state


def _signals(**overrides):
    base = dict(tier0_emergency=False, unresolved_important_contradiction=False, dangerous_diagnosis_not_excludable=False, evidence_conflict_unresolved=False, required_tool_unavailable=False, case_outside_scope=False, missing_info_would_change_ranking=False, has_sufficient_differential=False)
    base.update(overrides)
    return CaseSignals(**base)


class TestOutputStateMachine(unittest.TestCase):
    def test_emergency_takes_priority_over_everything_else(self):
        self.assertEqual(next_review_state(_signals(tier0_emergency=True, case_outside_scope=True, has_sufficient_differential=True)), ReviewState.EMERGENCY)

    def test_unresolved_contradiction_routes_to_human_review(self):
        self.assertEqual(next_review_state(_signals(unresolved_important_contradiction=True)), ReviewState.HUMAN_REVIEW)

    def test_dangerous_diagnosis_routes_to_human_review(self):
        self.assertEqual(next_review_state(_signals(dangerous_diagnosis_not_excludable=True)), ReviewState.HUMAN_REVIEW)

    def test_evidence_conflict_routes_to_abstain(self):
        self.assertEqual(next_review_state(_signals(evidence_conflict_unresolved=True)), ReviewState.ABSTAIN)

    def test_missing_tool_routes_to_abstain(self):
        self.assertEqual(next_review_state(_signals(required_tool_unavailable=True)), ReviewState.ABSTAIN)

    def test_missing_info_routes_to_more_information_needed(self):
        self.assertEqual(next_review_state(_signals(missing_info_would_change_ranking=True)), ReviewState.MORE_INFORMATION_NEEDED)

    def test_sufficient_differential(self):
        self.assertEqual(next_review_state(_signals(has_sufficient_differential=True)), ReviewState.DIFFERENTIAL)

    def test_default_is_info_only(self):
        self.assertEqual(next_review_state(_signals()), ReviewState.INFO_ONLY)

    def test_no_state_named_diagnosis_exists(self):
        self.assertNotIn("DIAGNOSIS", {s.value for s in ReviewState})


if __name__ == "__main__":
    unittest.main()
