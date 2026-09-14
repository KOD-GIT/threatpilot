import sys
import actions.agent_actions


def list_scenarios():
    print("Available scenarios:")
    for name in actions.agent_actions.scenarios.keys():
        print(f"  - {name}")


def _load_agents_and_tools():
    try:
        import autogen
        import autogen.runtime_logging
        from agents import text_agents, caldera_agents, code_agents
        from agents.coordinator_agents import task_coordinator_agent
        from utils.logs import print_usage_statistics
        from utils.shared_config import clean_working_directory
        import warnings
        return (
            autogen,
            text_agents,
            caldera_agents,
            code_agents,
            task_coordinator_agent,
            print_usage_statistics,
            clean_working_directory,
            warnings,
        )
    except ImportError as e:
        print(f"\n[!] Missing dependency: {e}", file=sys.stderr)
        print("    Please install dependencies via: pip install -r requirements.txt\n", file=sys.stderr)
        sys.exit(1)


def init_agents(text_agents, caldera_agents, code_agents, clean_working_directory, warnings):
    # Suppress UserWarnings for cleaner output
    warnings.filterwarnings("ignore", category=UserWarning)

    # Clean working directories
    clean_working_directory("caldera")
    clean_working_directory("pdf")
    clean_working_directory("code")

    # Register tools
    text_agents.register_tools()
    caldera_agents.register_tools()
    code_agents.register_tools()


def retrieve_agent(agent_name, text_agents, caldera_agents, code_agents):
    if agent_name == "caldera_agent":
        return caldera_agents.caldera_agent
    elif agent_name == "internet_agent":
        return text_agents.internet_agent
    elif agent_name == "text_analyst_agent":
        return text_agents.text_analyst_agent
    elif agent_name == "cmd_exec_agent":
        return code_agents.cmd_exec_agent
    else:
        return None


def run_scenario(scenario_name):
    available = list(actions.agent_actions.scenarios.keys())
    if scenario_name not in available:
        print(f"Scenario '{scenario_name}' not found.")
        list_scenarios()
        sys.exit(1)

    import utils.constants
    utils.constants.warn_missing_required_env()

    (
        autogen,
        text_agents,
        caldera_agents,
        code_agents,
        task_coordinator_agent,
        print_usage_statistics,
        clean_working_directory,
        warnings,
    ) = _load_agents_and_tools()

    init_agents(text_agents, caldera_agents, code_agents, clean_working_directory, warnings)

    scenario_agents = []
    scenario_messages = []
    scenario_tasks = []

    scenario_action_names = actions.agent_actions.scenarios[scenario_name]

    for scenario_action_name in scenario_action_names:
        for scenario_action in actions.agent_actions.actions.get(
            scenario_action_name, []
        ):
            scenario_agents.append(scenario_action["agent"])
            scenario_messages.append(scenario_action["message"])

            scenario_task = {
                "recipient": retrieve_agent(
                    scenario_action["agent"], text_agents, caldera_agents, code_agents
                ),
                "message": scenario_action["message"],
                "silent": False,
            }

            if "clear_history" in scenario_action:
                scenario_task["clear_history"] = scenario_action["clear_history"]
            else:
                scenario_task["clear_history"] = True

            if "summary_prompt" in scenario_action:
                scenario_task["summary_prompt"] = scenario_action["summary_prompt"]

            if "summary_method" in scenario_action:
                scenario_task["summary_method"] = scenario_action["summary_method"]

            if "carryover" in scenario_action:
                scenario_task["carryover"] = scenario_action["carryover"]

            scenario_tasks.append(scenario_task)

    if scenario_tasks:
        logging_session_id = autogen.runtime_logging.start(config={"dbname": "logs.db"})
        task_coordinator_agent.initiate_chats(scenario_tasks)
        autogen.runtime_logging.stop()
        print_usage_statistics(logging_session_id)
    else:
        print("No tasks configured for this scenario.")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h", "list", "--list"):
        print(f"Usage: python {sys.argv[0]} <scenario-name>\n")
        list_scenarios()
        sys.exit(0)

    scenario_to_run = sys.argv[1]
    run_scenario(scenario_to_run)
