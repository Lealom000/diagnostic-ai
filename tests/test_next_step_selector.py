import unittest

from core.next_step_selector import rank_next_steps


class TestNextStepSelector(unittest.TestCase):
    def test_tier0_ranked_first(self):
        items = [{"variable": "diet_history", "tier": 4}, {"variable": "oxygen_saturation", "tier": 0}]
        self.assertEqual(rank_next_steps(items)[0]["variable"], "oxygen_saturation")

    def test_dangerous_diagnosis_elimination_beats_general_discriminating(self):
        items = [{"variable": "x", "tier": 2, "discriminating_power": "high"}, {"variable": "d-dimer", "tier": 2, "eliminates_dangerous_diagnosis": True}]
        self.assertEqual(rank_next_steps(items)[0]["variable"], "d-dimer")

    def test_low_cost_beats_contradiction_resolution(self):
        items = [{"variable": "resolve-conflict", "tier": 2, "resolves_contradiction": True}, {"variable": "cheap-test", "tier": 2, "cost_risk": "low"}]
        self.assertEqual(rank_next_steps(items)[0]["variable"], "cheap-test")

    def test_all_entries_marked_recommended_only(self):
        self.assertEqual(rank_next_steps([{"variable": "x", "tier": 4}])[0]["status"], "recommended_only")

    def test_input_list_not_mutated(self):
        items = [{"variable": "x", "tier": 4}]
        rank_next_steps(items)
        self.assertNotIn("status", items[0])

    def test_empty_input(self):
        self.assertEqual(rank_next_steps([]), [])


if __name__ == "__main__":
    unittest.main()
