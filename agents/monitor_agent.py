"""
agents/monitor_agent.py
------------------------
MONITOR AGENT — Goal-Based Architecture
========================================
Prometheus Phase 2: Agent Type = MonitorAgent
Architecture justification: Goal-based because it has a PERSISTENT
GOAL — "keep all patients within safe vital bounds" — which it pursues
proactively. Unlike a reflex agent, it maintains state (which patients
it's watching) and checks them continuously. Unlike BDI, it doesn't
need complex multi-goal deliberation — one persistent goal is enough.

Prometheus Phase 3 Capability Diagram:
  Triggering Events       → Plans                → Beliefs/Data
  subscribe_request       → register_patient      → subscribed_patients
  periodic check (10s)    → check_vitals          → vitals_thresholds
  threshold crossed       → trigger_deterioration → alert_history
"""

import json
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
from datetime import datetime, timedelta

from protocols.messages import (
    ONT_SUBSCRIBE,
    make_deterioration_msg
)
from environment.sensors import random_deterioration
from beliefs.data import PatientVitals

# ── Vital sign thresholds (the agent's "goal condition") ──────────
# If any vital crosses these bounds the patient is deteriorating.
THRESHOLDS = {
    "spo2_min":     92,
    "hr_max":       130,
    "hr_min":       40,
    "bp_sys_min":   85,
    "rr_max":       30,
    "temp_max":     39.5,
}


class MonitorAgent(Agent):

    async def setup(self):
        # ── BELIEFS ────────────────────────────────────────────────
        # Dict of patient_id → PatientVitals being watched
        self.subscribed_patients: dict[str, dict] = {}
        self.deterioration_fired: set[str] = set()  # avoid repeated alerts

        print(f"\033[95m[MonitorAgent]\033[0m Online. Watching for deterioration...")

        self.add_behaviour(self.SubscribeBehaviour())
        # Periodic plan: check vitals every 8 seconds
        self.add_behaviour(self.CheckVitalsBehaviour(period=8))

    # ════════════════════════════════════════════════════════════════
    # PLAN: register_patient
    # Triggered by: subscribe_request event (from TriageAgent)
    # ════════════════════════════════════════════════════════════════
    class SubscribeBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if not msg:
                return
            if msg.get_metadata("ontology") != ONT_SUBSCRIBE:
                return

            data = json.loads(msg.body)
            pid = data["patient_id"]
            self.agent.subscribed_patients[pid] = data["vitals"]
            print(f"\033[95m[MonitorAgent]\033[0m Subscribed to {pid} "
                  f"({len(self.agent.subscribed_patients)} patients watched)")

    # ════════════════════════════════════════════════════════════════
    # PLAN: check_vitals (periodic — runs every 8 seconds)
    # This is the proactive goal-pursuit behaviour.
    # The agent checks ALL watched patients without waiting for an event.
    # ════════════════════════════════════════════════════════════════
    class CheckVitalsBehaviour(PeriodicBehaviour):
        async def run(self):
            if not self.agent.subscribed_patients:
                return

            print(f"\033[95m[MonitorAgent]\033[0m Checking "
                  f"{len(self.agent.subscribed_patients)} patient(s)...")

            for pid, vitals in list(self.agent.subscribed_patients.items()):
                if pid in self.agent.deterioration_fired:
                    continue  # already alerted, don't spam

                # ── Check goal condition (are vitals safe?) ───────
                deteriorated = self._check_thresholds(vitals)

                if deteriorated:
                    # Simulate new IoT reading that is worse
                    fake_vitals = PatientVitals(
                        patient_id=pid,
                        heart_rate=vitals["heart_rate"],
                        spo2=vitals["spo2"],
                        systolic_bp=vitals.get("systolic_bp", 110),
                        respiratory_rate=vitals.get("respiratory_rate", 18),
                        temperature=vitals.get("temperature", 37.0),
                        chief_complaint="",
                    )
                    worse = random_deterioration(fake_vitals)
                    new_v = {
                        "heart_rate": worse.heart_rate,
                        "spo2":       worse.spo2,
                    }

                    print(f"\033[95m[MonitorAgent]\033[0m !! Deterioration detected "
                          f"for {pid}: SpO2={worse.spo2}% HR={worse.heart_rate}")

                    # ── ACT: send deterioration alert to TriageAgent ──
                    alert = make_deterioration_msg(pid, new_v)
                    await self.send(alert)
                    self.agent.deterioration_fired.add(pid)
                    print(f"\033[95m[MonitorAgent]\033[0m → INFORM TriageAgent: "
                          f"DETERIORATION_ALERT for {pid}")

        def _check_thresholds(self, vitals: dict) -> bool:
            """Returns True if any vital is outside safe bounds."""
            if vitals.get("spo2", 100) < THRESHOLDS["spo2_min"]:
                return True
            if vitals.get("heart_rate", 70) > THRESHOLDS["hr_max"]:
                return True
            if vitals.get("heart_rate", 70) < THRESHOLDS["hr_min"]:
                return True
            return False
