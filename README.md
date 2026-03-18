# Smart Hospital Triage Agent System

## Overview
This project simulates a smart hospital triage system using intelligent agents. It demonstrates agent-based communication, resource allocation, and patient monitoring in a hospital environment.

## Features
- Four SPADE agents: Triage, Resource, Notification, Monitor
- Mock EMR database and bed registry
- CLI for manual patient admission and vitals update
- Demo mode with pre-defined patient scenarios
- Agent communication via FIPA-ACL messages

## Getting Started
### Prerequisites
- Python 3.10 or 3.11 (recommended)
- pip (Python package manager)

### Installation
1. Clone the repository:
	 ```bash
	 git clone <repo-url>
	 cd smart_hospital_triage_agent_system
	 ```
2. Install dependencies:
	 ```bash
	 pip install -r requirements.txt
	 ```

### Running the System
- Start the main demo:
	```bash
	python3 main.py
	```
- Admit patients manually:
	```bash
	python3 manual_admit.py
	```

## Troubleshooting
- SPADE errors with Python 3.12+: Use Python 3.10/3.11
- Check `system.log` for audit trail

## Project Structure
- `agents/` — Agent implementations
- `beliefs/` — Data models and agent beliefs
- `environment/` — EMR and sensor simulation
- `protocols/` — Message definitions
- `main.py` — Main demo entry point
- `manual_admit.py` — Manual admission CLI

## License
See LICENSE file for details.

## Contact
For questions or improvements, see code comments and logs.