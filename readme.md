# ThreatPilot: Multi-Agent Cybersecurity Automation System

> **Student Final Year / Capstone Project**  
> An automated purple teaming and cybersecurity assessment framework using collaborative AI agents.

---

## 📌 About The Project

As part of my computer science / cybersecurity project, I developed **ThreatPilot**—an automated framework that explores how multiple specialized Large Language Model (LLM) agents can work together to perform security tasks.

In traditional security operations, purple teaming requires manual effort to simulate attacks, review threat intelligence reports, and check whether defenses detected the activity. This project demonstrates how autonomous agents can coordinate to:
- Read threat reports and identify attacker tactics and techniques.
- Connect with Caldera to simulate security checks.
- Inspect system services and detect telemetry blind spots.
- Run shell commands in a safe, sandboxed directory.
- Summarize findings into clear structured reports.

---

## 🤖 Agent Roles

The framework consists of a coordinator agent that delegates tasks to specialized worker agents:

| Agent Name | Role | What It Does |
|---|---|---|
| `task_coordinator_agent` | Team Lead / Orchestrator | Coordinates the workflow, assigns tasks, and executes tool calls. |
| `text_analyst_agent` | Security Analyst | Summarizes security data, compares findings, and produces clean markdown tables. |
| `internet_agent` | Web & Intel Researcher | Fetches online threat advisories, advisory reports, and EDR detection datasets. |
| `cmd_exec_agent` | Command Runner | Executes terminal commands inside an isolated working folder. |
| `caldera_agent` | Caldera Operator | Interacts with the Caldera API to inspect agents, operations, and abilities. |

---

## 🛠️ System Architecture

```text
                     ┌───────────────────────┐
                     │   User CLI Command    │
                     │    (run_agents.py)    │
                     └───────────┬───────────┘
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │  Coordinator Agent    │
                     └───────────┬───────────┘
                                 │
     ┌───────────────────────────┼───────────────────────────┐
     ▼                           ▼                           ▼
┌───────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ Internet      │       │ Caldera Agent   │       │ Command Runner  │
│ Agent         │       │ (C2 Operations) │       │ (Local Sandbox) │
└───────┬───────┘       └────────┬────────┘       └────────┬────────┘
        │                        │                         │
        └────────────────────────┼─────────────────────────┘
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │  Text Analyst Agent   │
                     │  (Final Summary/Log)  │
                     └───────────────────────┘
```

---

## 🧪 Available Scenarios

The project includes pre-built test scenarios defined in `actions/agent_actions.py`:

- **`HELLO_AGENTS`**: Basic test to verify that the agents and LLM connection are functioning properly.
- **`SUMMARIZE_RECENT_CISA_VULNS`**: Downloads the latest known exploited vulnerabilities feed and extracts key details.
- **`HELLO_CALDERA`**: Sends a test pop-up message to an active Caldera agent via PowerShell.
- **`COLLECT_CALDERA_INFO`**: Retrieves active Caldera operation IDs and agent details.
- **`DETECT_EDR`**: Checks running Windows services against known security software signatures.
- **`DETECT_AGENT_PRIVILEGES`**: Checks the user privilege level (Standard, Administrator, or System) on the agent host.
- **`IDENTIFY_EDR_BYPASS_TECHNIQUES`**: Identifies detection telemetry gaps for specific security software.
- **`TTP_REPORT_TO_TECHNIQUES`**: Downloads an online threat report and extracts attacker techniques.
- **`TTP_REPORT_TO_ADVERSARY_PROFILE`**: Converts extracted techniques from a threat report into a Caldera adversary profile.

---

## 🚀 Setup & How to Run

### Prerequisites
- Python 3.10+ (or Docker)
- OpenAI API Key

---

### Method 1: Running Locally with Python

#### Step 1: Install dependencies
```bash
pip install -r requirements.txt
```

#### Step 2: Set up your environment file
Copy the template file to `.env`:
```bash
cp .env_template .env
```
Open `.env` and fill in your OpenAI API Key:
```env
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL_NAME=gpt-4o-mini
```

#### Step 3: Check available scenarios
You can list all scenarios at any time:
```bash
python run_agents.py --list
```

#### Step 4: Run a scenario
Run the basic test scenario:
```bash
python run_agents.py HELLO_AGENTS
```
Or run any of the other scenarios:
```bash
python run_agents.py SUMMARIZE_RECENT_CISA_VULNS
```

*(Optional)* If you want to run the local demo HTTP and FTP servers:
```bash
python run_servers.py
```

---

### Method 2: Running with Docker

You can also run the entire project in an isolated container without installing dependencies on your host machine:

1. Configure `.env`:
   ```bash
   cp .env_template .env
   ```
2. Run any scenario with Docker Compose:
   ```bash
   docker compose run --rm threatpilot HELLO_AGENTS
   ```
3. Or build and run with Docker directly:
   ```bash
   docker build -t threatpilot .
   docker run --rm --env-file .env threatpilot HELLO_AGENTS
   ```

---

## 📁 Project Structure

```
├── actions/
│   └── agent_actions.py      # Scenario actions and task messages
├── agents/
│   ├── coordinator_agents.py # Coordinator agent definition
│   ├── text_agents.py        # Text analysis & internet research agents
│   ├── code_agents.py        # Terminal command runner agent
│   └── caldera_agents.py     # Caldera integration agent
├── tools/
│   ├── caldera_tools.py      # Functions for calling Caldera API
│   ├── code_tools.py         # Subprocess command execution tool
│   └── web_tools.py          # Web content download tools
├── utils/
│   ├── constants.py          # Environment configuration loader
│   ├── ftp_server.py         # Local FTP server for demo file transfers
│   ├── logs.py               # Token usage & cost tracking with SQLite
│   ├── shared_config.py      # Shared LLM settings and directory cleaners
│   └── web_server.py         # Local HTTP server for demo file downloads
├── tests/
│   └── test_threatpilot.py   # Unit tests for scenarios and directories
├── .env_template             # Sample configuration file
├── Dockerfile                # Docker container build configuration
├── docker-compose.yml        # Docker compose setup
├── requirements.txt          # Python dependencies
├── run_agents.py             # Main program entry point
└── run_servers.py            # Script to launch demo HTTP & FTP servers
```

---

## ⚠️ Notes & Lab Safety

- Always run LLM-generated code in a virtual machine, sandbox, or Docker container.
- API token usage and estimated costs are logged automatically to `logs.db` after each run.
