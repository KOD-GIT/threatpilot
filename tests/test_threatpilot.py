import unittest
import os
import actions.agent_actions
from utils.shared_config import clean_working_directory, working_folder


class TestThreatPilotStructure(unittest.TestCase):
    def test_scenarios_exist(self):
        """Verify scenarios dictionary is populated."""
        self.assertGreater(len(actions.agent_actions.scenarios), 0)

    def test_actions_exist(self):
        """Verify actions dictionary is populated."""
        self.assertGreater(len(actions.agent_actions.actions), 0)

    def test_scenarios_reference_valid_actions(self):
        """Ensure all scenario action names map to defined actions."""
        valid_agents = {
            "caldera_agent",
            "internet_agent",
            "text_analyst_agent",
            "cmd_exec_agent",
        }
        for scenario_name, action_list in actions.agent_actions.scenarios.items():
            self.assertIsInstance(action_list, list, f"{scenario_name} actions must be a list")
            for action_name in action_list:
                self.assertIn(
                    action_name,
                    actions.agent_actions.actions,
                    f"Scenario '{scenario_name}' references undefined action '{action_name}'",
                )
                for step in actions.agent_actions.actions[action_name]:
                    self.assertIn("agent", step)
                    self.assertIn("message", step)
                    self.assertIn(
                        step["agent"],
                        valid_agents,
                        f"Unknown agent '{step['agent']}' in action '{action_name}'",
                    )

    def test_clean_working_directory_safety(self):
        """Ensure clean_working_directory creates and cleans subfolders safely."""
        test_subfolder = "test_dir_safe"
        clean_working_directory(test_subfolder)
        target = os.path.join(working_folder, test_subfolder)
        self.assertTrue(os.path.exists(target))
        # Create a test file
        test_file = os.path.join(target, "sample.txt")
        with open(test_file, "w") as f:
            f.write("test content")
        self.assertTrue(os.path.exists(test_file))
        # Clean should remove the file
        clean_working_directory(test_subfolder)
        self.assertFalse(os.path.exists(test_file))
        # Cleanup test folder
        if os.path.exists(target):
            os.rmdir(target)


if __name__ == "__main__":
    unittest.main()
