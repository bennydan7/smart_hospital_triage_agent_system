# DCIT 403 Intelligent Agent Project – Presentation Guide

## Title Slide
**Project Title:** Smart Hospital Triage Agent System  
**Student Name:** [Your Name]  
**Course:** DCIT 403 – Intelligent Agent Systems

---

## 1. Problem Description
Modern hospitals face critical challenges in triaging patients efficiently, especially during surges or emergencies. Manual triage is slow, error-prone, and can lead to poor outcomes. An agent-based system can automate, accelerate, and optimize triage, resource allocation, and escalation, ensuring the right care at the right time.

---

## 2. Goal Specification
- **Top-level Goal:**
  - Automate and optimize patient triage and resource allocation in a hospital emergency setting.
- **Sub-goals:**
  - Rapidly assess patient severity (ESI levels)
  - Allocate beds and staff efficiently
  - Monitor patient deterioration and escalate care
  - Notify appropriate staff instantly

---

## 3. Functionalities
- Automated triage based on patient vitals and complaints
- Dynamic bed allocation and escalation
- Real-time monitoring and alerting for patient deterioration
- Interactive patient admission (CLI)
- Manual override for vitals (simulate emergencies)
- Persistent logging for audit and review

---

## 4. Environment Description
- **Percepts:**
  - Patient arrivals (vitals, complaints)
  - Bed availability
  - Patient vital sign changes (from sensors or manual input)
- **Actions:**
  - Assign ESI level and ward
  - Request/allocate beds
  - Notify staff
  - Escalate care if patient deteriorates

---

## 5. Agent Architecture
- **Agents:**
  - TriageAgent (BDI)
  - ResourceAgent (Utility-based)
  - NotificationAgent (Reflex)
  - MonitorAgent (Goal-based)
- **Justification:**
  - Each agent type matches its real-world hospital role and Prometheus methodology.

---

## 6. Agent Communication
- **Acquaintance Diagram:**
  - TriageAgent ↔ ResourceAgent ↔ MonitorAgent ↔ NotificationAgent
- **Information Flow:**
  - All communication via FIPA-ACL messages (no direct calls)
  - Ontology tags route messages to correct behaviours

---

## 7. Interaction Design
- **Message Sequence Example:**
  1. ControllerAgent sends INFORM to TriageAgent (new patient)
  2. TriageAgent REQUESTs bed from ResourceAgent
  3. ResourceAgent CONFIRMs or FAILS
  4. TriageAgent informs NotificationAgent and subscribes MonitorAgent
  5. MonitorAgent sends DETERIORATION_ALERT if needed
  6. TriageAgent escalates if patient worsens

---

## 8. Detailed Design
- **Capabilities:**
  - Perceive (receive messages)
  - Decide (apply ESI rules, allocate resources)
  - Act (send messages, update beliefs)
- **Plans:**
  - Each agent has plans mapped to Prometheus diagrams
- **Beliefs/Data:**
  - Patient vitals, triage records, bed registry, alert logs

---

## 9. Implementation & Demo
- **Prototype:**
  - Python SPADE agents, CLI interface, persistent logging
- **Demo Steps:**
  1. Start system: `python3 main.py`
  2. Demo patients processed in parallel
  3. Admit new patients interactively
  4. Manually update vitals to trigger escalation
  5. Show logs and final triage summary

---

## 10. Challenges & Limitations
- SPADE/Python 3.12 XML errors (workaround: robust error handling)
- No real sensor integration (manual/CLI input used)
- No web dashboard (future work)
- Limited to CLI for demo

---

## 11. Presentation Script (What to Say)

### Slide 1: Title
"Good [morning/afternoon], my name is [Your Name]. My project is the Smart Hospital Triage Agent System for DCIT 403."

### Slide 2: Problem
"Hospitals struggle with fast, accurate triage, especially in emergencies. Manual triage can be slow and error-prone. An agent-based system can automate and optimize this process."

### Slide 3: Goals
"The main goal is to automate triage and resource allocation. Sub-goals include rapid assessment, efficient bed allocation, real-time monitoring, and instant staff notification."

### Slide 4: Functionalities
"The system can triage patients, allocate beds, monitor for deterioration, allow interactive admissions, and log all actions."

### Slide 5: Environment
"The environment includes patient arrivals, bed status, and vital sign changes as percepts. Actions include assigning ESI, allocating beds, notifying staff, and escalating care."

### Slide 6: Architecture
"There are four agents: Triage, Resource, Notification, and Monitor. Each uses a different agent architecture matching its real-world role."

### Slide 7: Communication
"Agents communicate only via FIPA-ACL messages, never direct calls. The acquaintance diagram shows the information flow."

### Slide 8: Interaction
"A typical message sequence: Controller sends a new patient, Triage requests a bed, Resource confirms, Triage notifies staff and subscribes Monitor, Monitor alerts if needed, and Triage escalates if the patient worsens."

### Slide 9: Detailed Design
"Each agent's plans and beliefs are mapped to Prometheus artifacts. The Perceive–Decide–Act loop is visible in the logs."

### Slide 10: Implementation & Demo
"I'll now run the system. Demo patients are processed in parallel. I can admit new patients and manually update vitals to trigger escalation. All actions are logged."

### Slide 11: Challenges
"Challenges included SPADE/Python compatibility and lack of real sensors. I used robust error handling and CLI input as workarounds."

### Slide 12: Q&A
"Thank you for your attention. I'm happy to take any questions."

---

## 12. Tips for Presentation
- Practice the demo steps in advance.
- Keep each slide focused and concise.
- Use the logs and CLI to show real agent actions.
- Be ready to explain the Perceive–Decide–Act loop and Prometheus mapping.
- End with a confident summary and invite questions.

---

**Good luck with your presentation!**
