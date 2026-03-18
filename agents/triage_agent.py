"""
agents/triage_agent.py
----------------------
TRIAGE AGENT — BDI Deliberative Architecture
============================================
Prometheus Phase 2: Agent Type = TriageAgent
Architecture justification: BDI is needed because this agent must
deliberate across multiple plans when ESI boundaries are ambiguous,
maintain beliefs about patients over time, and handle competing goals
(speed vs accuracy in triage classification).

Prometheus Phase 3 Capability Diagram:
  Triggering Events → Plans → Beliefs/Data

  new_patient_arrival  →  fast_triage         → patient_vitals, esi_rule_table
  bed_confirmed        →  complete_triage      → triage_history, current_triage
  bed_failure          →  handle_no_bed        → waiting_list
  deterioration_alert  →  retriage             → patient_vitals (updated)

Percept → Decide → Act loop:
  PERCEIVE : receive patient registration message (FIPA INFORM)
  DECIDE   : apply ESI rule table to vitals → select plan
  ACT      : send bed REQUEST to ResourceAgent + SUBSCRIBE MonitorAgent
"""

import json
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

from beliefs.data import (
    PatientVitals, TriageRecord,
    apply_esi_rules, get_target_ward,
    ESI_LABELS, ESI_COLOURS, RESET
)
from protocols.messages import (
    ONT_REGISTER, ONT_BED_CONFIRM, ONT_BED_FAILURE, ONT_DETERIORATION,
    make_bed_request_msg, make_triage_result_msg, make_subscribe_msg
)
from environment.emr import log_triage


class TriageAgent(Agent):
    """
    The central BDI agent. Runs three concurrent behaviours (plans):
      1. ReceivePatientBehaviour   – PERCEIVE new arrivals
      2. ReceiveBedConfirmBehaviour – PERCEIVE bed allocation results
      3. ReceiveDeteriorationBehaviour – PERCEIVE monitor alerts
    """

    async def setup(self):
        # ── BELIEFS ────────────────────────────────────────────────
        # These are the agent's internal world model (Phase 3 beliefs)
        self.patient_vitals: dict[str, PatientVitals] = {}
        self.triage_records: dict[str, TriageRecord] = {}
        self.waiting_list: list[str] = []   # patients with no bed yet

        print(f"\033[94m[TriageAgent]\033[0m Online. Waiting for patients...")

        # ── REGISTER BEHAVIOURS (plans) ───────────────────────────
        self.add_behaviour(self.ReceivePatientBehaviour())
        self.add_behaviour(self.ReceiveBedConfirmBehaviour())
        self.add_behaviour(self.ReceiveDeteriorationBehaviour())

    # ════════════════════════════════════════════════════════════════
    # PLAN 1: fast_triage
    # Triggered by: new_patient_arrival event
    # This implements the full Percept → Decide → Act loop
    # ════════════════════════════════════════════════════════════════
    class ReceivePatientBehaviour(CyclicBehaviour):
        async def run(self):
            # ── PERCEIVE ──────────────────────────────────────────
            msg = await self.receive(timeout=5)
            if not msg:
                return
            if msg.get_metadata("ontology") != ONT_REGISTER:
                return

            data = json.loads(msg.body)
            vitals = PatientVitals(**data)

            # Update beliefs with new percept
            self.agent.patient_vitals[vitals.patient_id] = vitals

            print(f"\n\033[94m[TriageAgent]\033[0m ── PERCEIVE ──────────────────")
            print(f"  Patient {vitals.patient_id} arrived: {vitals.chief_complaint}")
            print(f"  HR={vitals.heart_rate} SpO2={vitals.spo2}% "
                  f"BP={vitals.systolic_bp} RR={vitals.respiratory_rate} "
                  f"Temp={vitals.temperature}°C")

            # ── DECIDE ───────────────────────────────────────────
            # Fire the ESI rule table against current beliefs
            esi = apply_esi_rules(vitals)
            ward = get_target_ward(esi)
            escalated = esi <= 2

            col = ESI_COLOURS.get(esi, "")
            print(f"\033[94m[TriageAgent]\033[0m ── DECIDE ───────────────────")
            print(f"  ESI rules fired → {col}{ESI_LABELS[esi]}{RESET}")
            print(f"  Target ward: {ward} | Escalate: {escalated}")

            # Create triage record belief
            record = TriageRecord(
                patient_id=vitals.patient_id,
                esi_level=esi,
                escalated=escalated,
            )
            self.agent.triage_records[vitals.patient_id] = record

            # ── ACT ──────────────────────────────────────────────
            print(f"\033[94m[TriageAgent]\033[0m ── ACT ──────────────────────")

            # Action 1: Request bed from ResourceAgent
            bed_req = make_bed_request_msg(vitals.patient_id, esi, ward)
            await self.send(bed_req)
            print(f"  → REQUEST bed in {ward} for {vitals.patient_id}")

            # Action 2: Subscribe MonitorAgent to track this patient
            vitals_dict = {
                "heart_rate": vitals.heart_rate,
                "spo2": vitals.spo2,
                "systolic_bp": vitals.systolic_bp,
                "respiratory_rate": vitals.respiratory_rate,
                "temperature": vitals.temperature,
            }
            sub_msg = make_subscribe_msg(vitals.patient_id, vitals_dict)
            await self.send(sub_msg)
            print(f"  → SUBSCRIBE MonitorAgent for {vitals.patient_id}")

    # ════════════════════════════════════════════════════════════════
    # PLAN 2: complete_triage
    # Triggered by: bed_confirmed event (ResourceAgent replies)
    # ════════════════════════════════════════════════════════════════
    class ReceiveBedConfirmBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if not msg:
                return

            ont = msg.get_metadata("ontology")

            if ont == ONT_BED_CONFIRM:
                data = json.loads(msg.body)
                pid = data["patient_id"]

                # Belief revision: update triage record with bed assignment
                if pid in self.agent.triage_records:
                    record = self.agent.triage_records[pid]
                    record.assigned_bed = data["bed_id"]
                    record.assigned_ward = data["ward"]

                    print(f"\n\033[94m[TriageAgent]\033[0m Bed confirmed for {pid}: "
                          f"{data['bed_id']} in {data['ward']}")

                    # Action: Inform NotificationAgent of final triage result
                    result_msg = make_triage_result_msg(record)
                    await self.send(result_msg)
                    print(f"\033[94m[TriageAgent]\033[0m → INFORM NotificationAgent "
                          f"(ESI-{record.esi_level}, {data['bed_id']})")

                    # Action: Write to EMR
                    log_triage(record)
                    print(f"\033[94m[TriageAgent]\033[0m → Updated EMR record")

            elif ont == ONT_BED_FAILURE:
                # ── PLAN: handle_no_bed ───────────────────────────
                data = json.loads(msg.body)
                pid = data["patient_id"]
                self.agent.waiting_list.append(pid)
                print(f"\n\033[94m[TriageAgent]\033[0m ⚠ No bed in {data['ward']} "
                      f"for {pid}. Added to waiting list.")

    # ════════════════════════════════════════════════════════════════
    # PLAN 3: retriage
    # Triggered by: deterioration_alert event (MonitorAgent)
    # Demonstrates belief revision and re-triggering plans
    # ════════════════════════════════════════════════════════════════
    class ReceiveDeteriorationBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if not msg:
                return
            if msg.get_metadata("ontology") != ONT_DETERIORATION:
                return

            data = json.loads(msg.body)
            pid = data["patient_id"]
            new_v = data["new_vitals"]

            print(f"\n\033[91m[TriageAgent]\033[0m !! DETERIORATION ALERT for {pid}")

            # ── Belief Revision ───────────────────────────────────
            # Update stored vitals belief with new readings
            if pid in self.agent.patient_vitals:
                old = self.agent.patient_vitals[pid]
                old.heart_rate = new_v["heart_rate"]
                old.spo2 = new_v["spo2"]
                print(f"\033[91m[TriageAgent]\033[0m  Belief revised: "
                      f"HR {new_v['heart_rate']} | SpO2 {new_v['spo2']}%")

                # ── Re-DECIDE ─────────────────────────────────────
                new_esi = apply_esi_rules(old)
                old_esi = self.agent.triage_records[pid].esi_level

                if new_esi < old_esi:  # lower number = more critical
                    print(f"\033[91m[TriageAgent]\033[0m  ESI UPGRADED: "
                          f"{old_esi} → {new_esi} ({ESI_LABELS[new_esi]})")

                    # ── Re-ACT ────────────────────────────────────
                    new_ward = get_target_ward(new_esi)
                    self.agent.triage_records[pid].esi_level = new_esi
                    self.agent.triage_records[pid].escalated = True

                    # Re-request a higher-priority bed
                    bed_req = make_bed_request_msg(pid, new_esi, new_ward)
                    await self.send(bed_req)
                    print(f"\033[91m[TriageAgent]\033[0m  → ESCALATE: REQUEST "
                          f"bed in {new_ward}")
                else:
                    print(f"\033[94m[TriageAgent]\033[0m  ESI unchanged ({old_esi})")
