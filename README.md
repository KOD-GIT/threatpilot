# ThreatPilot

ThreatPilot is a Python-based cybersecurity automation project that uses multiple LLM-powered agents to support purple-team style workflows. It can collect threat intelligence, inspect endpoint signals through a Caldera lab, execute controlled local commands, and turn the results into structured security summaries.

The project is designed as a practical demonstration of how agent coordination can reduce repetitive analysis work in a security assessment lab.

## Features

- Scenario-based command-line workflow
- Multi-agent task coordination using AutoGen
- Threat intelligence summarization from configurable data sources
- Caldera API integration for lab operations
- Endpoint service and privilege inspection scenarios
- MITRE ATT&CK technique extraction and Caldera ability matching
- Local HTTP and FTP demo servers for controlled lab exercises
- SQLite-based usage logging for LLM runs

## Architecture

```text
User command
    |
    v
run_agents.py
    |
    v
Task coordinator agent
    |
    +--> Internet agent       -> web and report collection
    +--> Caldera agent        -> lab API and endpoint actions
    +--> Command agent        -> local command execution
    +--> Text analyst agent   -> summaries and final reports
```

## Project Structure

```text
actions/
  agent_actions.py       Scenario definitions
agents/
  coordinator_agents.py  Main orchestration agent
  text_agents.py         Text analysis and web research agents
  code_agents.py         Local command execution agent
  caldera_agents.py      Caldera integration agent
tools/
  web_tools.py           Web and PDF download helpers
  code_tools.py          Local shell execution helper
  caldera_tools.py       Caldera API and operation helpers
utils/
  constants.py           Environment configuration
  shared_config.py       Shared LLM configuration and workspace cleanup
  logs.py                Runtime usage logging
  web_server.py          Local HTTP server
  ftp_server.py          Local FTP server
tests/
  test_threatpilot.py    Basic structure and utility tests
```

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Create a local environment file:

```bash
copy .env.example .env
```

Fill in only the values needed for the scenarios you plan to run. Keep `.env` private and never commit it.

Required for LLM scenarios:

```env
OPENAI_API_KEY=
OPENAI_MODEL_NAME=
```

Required for Caldera scenarios:

```env
CALDERA_SERVER=
CALDERA_API_KEY=
```

Optional local demo server settings:

```env
WEB_SERVER_PORT=8800
FTP_SERVER_ADDRESS=
FTP_SERVER_USER=
FTP_SERVER_PASS=
```

Optional scenario data sources:

```env
CISA_KEV_URL=
EDR_TELEMETRY_URL=
EDR_TELEMETRY_README_URL=
TECHNIQUE_REPORT_URL=
ADVERSARY_REPORT_URL=
```

## Usage

List available scenarios:

```bash
python run_agents.py --list
```

Run a scenario:

```bash
python run_agents.py HELLO_AGENTS
```

Start the optional local demo servers:

```bash
python run_servers.py
```

## Available Scenarios

- `HELLO_AGENTS`: verifies that the agent workflow and LLM connection are working.
- `SUMMARIZE_RECENT_CISA_VULNS`: collects vulnerability feed data and summarizes key entries.
- `COLLECT_CALDERA_INFO`: retrieves active Caldera operation and agent details.
- `HELLO_CALDERA`: sends a simple test command to an active Caldera agent.
- `DETECT_EDR`: compares endpoint services with known security tooling indicators.
- `DETECT_AGENT_PRIVILEGES`: checks the current privilege level of a Caldera agent.
- `IDENTIFY_EDR_BYPASS_TECHNIQUES`: identifies telemetry gaps for a selected EDR dataset.
- `TTP_REPORT_TO_TECHNIQUES`: extracts MITRE techniques from a configured threat report.
- `TTP_REPORT_TO_ADVERSARY_PROFILE`: maps extracted techniques to Caldera abilities and builds an adversary profile.

## Testing

Run the test suite:

```bash
python -m unittest -v tests.test_threatpilot
```

or:

```bash
pytest -q
```

## Safety Notes

This project is intended for controlled lab environments only. Some scenarios execute commands locally or through a Caldera agent. Run those scenarios in an isolated VM or test network, review commands before use, and avoid using production credentials or production endpoints.

## GitHub Checklist

Before publishing:

- Keep `.env` out of version control.
- Confirm that `.env.example` contains no real credentials.
- Remove generated folders such as `__pycache__`, `.pytest_cache`, and `llm_working_folder`.
- Run the tests.
- Review the scenario URLs configured in your local `.env`.
