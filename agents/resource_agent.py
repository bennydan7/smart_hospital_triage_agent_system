"""
agents/resource_agent.py
------------------------
RESOURCE AGENT — Utility-Based + Reactive Architecture
======================================================
Prometheus Phase 2: Agent Type = ResourceAgent
Architecture justification: Utility-based because it must OPTIMISE
bed allocation — when multiple ESI-2 patients compete for the same
ward, the agent assigns based on ESI priority (urgency × availability).
Reactive layer handles the fast condition-action bed assignment.

Prometheus Phase 3 Capability Diagram:
  Triggering Events    → Plans             → Beliefs/Data
  bed_request received → allocate_bed      → bed_registry (SQLite)
  bed_request, no bed  → handle_no_bed     → waiting_queue
"""

import json
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

from protocols.messages import (
    ONT_BED_REQUEST,
    make_bed_confirm_msg, make_bed_failure_msg
)
from environment.emr import query_available_bed, allocate_bed


class ResourceAgent(Agent):

    async def setup(self):
        # ── BELIEFS ────────────────────────────────────────────────
        self.waiting_queue: list[dict] = []   # patients waiting for beds
        print(f"\033[92m[ResourceAgent]\033[0m Online. Bed registry loaded.")
        self.add_behaviour(self.BedAllocationBehaviour())

    # ════════════════════════════════════════════════════════════════
    # PLAN: allocate_bed
    # Triggered by: bed_request event from TriageAgent
    # ════════════════════════════════════════════════════════════════
    class BedAllocationBehaviour(CyclicBehaviour):
        async def run(self):
            # ── PERCEIVE ─────────────────────────────────────────
            msg = await self.receive(timeout=5)
            if not msg:
                return
            if msg.get_metadata("ontology") != ONT_BED_REQUEST:
                return

            data = json.loads(msg.body)
            pid   = data["patient_id"]
            esi   = data["esi_level"]
            ward  = data["ward"]

            print(f"\n\033[92m[ResourceAgent]\033[0m ── PERCEIVE ─────────────────")
            print(f"  Bed REQUEST for {pid} | ESI-{esi} | Ward: {ward}")

            # ── DECIDE (utility calculation) ──────────────────────
            # Query the live bed registry (the agent's environment)
            bed_id = query_available_bed(ward)

            print(f"\033[92m[ResourceAgent]\033[0m ── DECIDE ───────────────────")
            if bed_id:
                print(f"  Available bed found: {bed_id} in {ward}")
            else:
                print(f"  No beds available in {ward}")

            # ── ACT ──────────────────────────────────────────────
            print(f"\033[92m[ResourceAgent]\033[0m ── ACT ──────────────────────")

            if bed_id:
                # Allocate the bed in the EMR database
                success = allocate_bed(bed_id, pid)
                if success:
                    reply = make_bed_confirm_msg(pid, bed_id, ward)
                    await self.send(reply)
                    print(f"  → CONFIRM: {bed_id} allocated to {pid}")
                else:
                    # Race condition: bed was just taken by another patient
                    reply = make_bed_failure_msg(pid, ward)
                    await self.send(reply)
                    print(f"  → FAILURE: race condition on {bed_id}")
            else:
                # No bed available — send failure to TriageAgent
                reply = make_bed_failure_msg(pid, ward)
                await self.send(reply)
                print(f"  → FAILURE: no beds in {ward} for {pid}")
                self.agent.waiting_queue.append(data)
