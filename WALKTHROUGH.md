# Smart Hospital Triage Agent System — Walkthrough & Presentation Guide

## How to Run the System

1. **Install dependencies:**
   - Ensure you have Python 3.12+ and run:
     ```bash
     pip install -r requirements.txt
     ```
   - (If SPADE errors persist, try Python 3.10/3.11 if possible.)

2. **Start the system:**
   ```bash
   python3 main.py
   ```
   This will:
   - Initialize the EMR database
   - Start all four agents (Triage, Resource, Notification, Monitor)
   - Run a demo with 5 pre-defined patients
   - Allow you to admit new patients interactively via CLI

3. **Admit new patients:**
   - After the demo, you will be prompted to enter new patient data (ID, vitals, complaint) as many times as you like.
   - Type `exit` to finish and see the final triage summary.

4. **Manual vitals update:**
   - While the system is running, you can update a patient's vitals in real time by typing in the MonitorAgent's CLI:
     ```
     update <patient_id> <heart_rate> <spo2>
     ```
   - Example: `update P003 120 85`

5. **Logs:**
   - All actions, decisions, and alerts are logged to `system.log` and printed to the console.

---

## What to Say When Presenting

### 1. **System Overview**
- "This is a multi-agent hospital triage simulation, designed using the Prometheus AOSE methodology."
- "Four agents run in parallel: Triage, Resource, Notification, and Monitor. They communicate only via FIPA-ACL messages, never by direct function calls."

### 2. **Demo Walkthrough**
- "On startup, the system runs a demo with 5 patients, each designed to trigger a different triage level."
- "After the demo, I can admit new patients interactively, simulating real hospital arrivals."
- "The MonitorAgent checks all patients' vitals every 8 seconds. If a patient deteriorates, it triggers an escalation and re-triage."
- "I can also manually update a patient's vitals in real time to simulate sudden changes."

### 3. **Key Features to Highlight**
- "All agent actions and decisions are logged to a file for audit and review."
- "The system is robust: errors are logged, and agents handle failures gracefully."
- "The architecture is scalable and modular, supporting parallel patient processing and easy extension."

### 4. **Prometheus Mapping**
- "Each agent's code directly maps to Prometheus artifacts: Events (messages), Plans (behaviours), and Beliefs (internal state)."
- "The Perceive–Decide–Act loop is visible in the logs for every patient."

---

## Example Demo Script

1. **Start the system:**
   - "Let's run the system."
2. **Show the demo patients being processed.**
   - "Here are the 5 demo patients, each triaged and assigned a bed."
3. **Admit a new patient interactively.**
   - "Now I'll admit a new patient with custom vitals."
4. **Trigger a deterioration manually.**
   - "I'll update this patient's vitals to simulate a sudden drop in SpO2. Watch the system escalate their care."
5. **Show the final triage summary.**
   - "Here's the final triage summary, showing all patients, their ESI levels, wards, beds, and any escalations."

---

## Troubleshooting
- If you see repeated XML errors, it's a known SPADE/Python 3.12 issue, but the system logic still works.
- For best results, use Python 3.10/3.11 if possible.
- Check `system.log` for a full audit trail of all actions.

---

## Extending the System
- Add a REST API for patient admission.
- Integrate with real sensor data for vitals.
- Add a web dashboard for visualization.
- Support more complex escalation and resource management logic.

---

**For questions or further improvements, see the code comments and logs.**
