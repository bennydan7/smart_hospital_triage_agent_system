"""
agents/notification_agent.py
-----------------------------
NOTIFICATION AGENT — Simple Reflex Architecture
================================================
Prometheus Phase 2: Agent Type = NotificationAgent
Architecture justification: Pure condition-action mapping.
IF triage_result(ESI=1) THEN alert(charge_nurse, CRITICAL)
IF triage_result(ESI=2) THEN alert(duty_doctor, URGENT)
No memory, no deliberation needed — speed is the only priority.
This agent has the simplest internal structure of all four agents.

Prometheus Phase 3 Capability Diagram:
  Triggering Events     → Plans            → Beliefs/Data
  triage_result received → send_alert      → alert_log, staff_contacts
"""

import json
import time
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

from beliefs.data import AlertRecord, ESI_LABELS, ESI_COLOURS, RESET
from protocols.messages import ONT_TRIAGE_RESULT
from environment.emr import log_alert


# ── Staff contacts (condition-action table) ───────────────────────
# This IS the agent's "rule table" — the entire intelligence of a
# reflex agent lives in this mapping.
STAFF_ROUTING = {
    1: ("Charge Nurse + Resus Team",  "CRITICAL — IMMEDIATE RESPONSE REQUIRED"),
    2: ("Duty Doctor + ICU Nurse",    "URGENT — respond within 10 minutes"),
    3: ("Ward Doctor",                "URGENT — respond within 30 minutes"),
    4: ("Triage Nurse",               "LESS URGENT — respond within 60 minutes"),
    5: ("Reception",                  "NON-URGENT — standard queue"),
}


class NotificationAgent(Agent):

    async def setup(self):
        # ── BELIEFS ────────────────────────────────────────────────
        self.alert_log: list[AlertRecord] = []
        print(f"\033[93m[NotifAgent]\033[0m Online. Staff routing table loaded.")
        self.add_behaviour(self.AlertBehaviour())

    # ════════════════════════════════════════════════════════════════
    # PLAN: send_alert
    # Triggered by: triage_result event (from TriageAgent)
    # This is the complete Percept → Decide → Act loop for a reflex agent.
    # The "decide" step is just a table lookup — no deliberation needed.
    # ════════════════════════════════════════════════════════════════
    class AlertBehaviour(CyclicBehaviour):
        async def run(self):
            # ── PERCEIVE ─────────────────────────────────────────
            msg = await self.receive(timeout=5)
            if not msg:
                return
            if msg.get_metadata("ontology") != ONT_TRIAGE_RESULT:
                return

            data = json.loads(msg.body)
            pid  = data["patient_id"]
            esi  = data["esi_level"]
            bed  = data.get("assigned_bed", "TBD")
            ward = data.get("assigned_ward", "TBD")

            # ── DECIDE (condition-action lookup — no deliberation) ─
            staff, urgency_msg = STAFF_ROUTING.get(esi, STAFF_ROUTING[5])

            col = ESI_COLOURS.get(esi, "")
            print(f"\n\033[93m[NotifAgent]\033[0m ── PERCEIVE + DECIDE ────────")
            print(f"  Triage result for {pid}: {col}{ESI_LABELS[esi]}{RESET}")
            print(f"  Condition matched → Route to: {staff}")

            # ── ACT ──────────────────────────────────────────────
            alert_text = (
                f"PATIENT {pid} | {ESI_LABELS[esi]} | "
                f"Bed: {bed} ({ward}) | {urgency_msg}"
            )

            # Simulate SMS / pager dispatch
            print(f"\033[93m[NotifAgent]\033[0m ── ACT ─────────────────────")
            print(f"  → ALERT sent to {staff}")
            print(f"  → Message: {alert_text}")

            # Belief update: log the alert
            record = AlertRecord(
                patient_id=pid,
                esi_level=esi,
                message=alert_text,
                sent_to=staff,
            )
            self.agent.alert_log.append(record)
            log_alert(record)
            print(f"\033[93m[NotifAgent]\033[0m → Alert logged to EMR")
