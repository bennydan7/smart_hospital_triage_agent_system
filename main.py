"""
main.py — Smart Hospital Triage Agent System
Run with: python3 main.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import asyncio
import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour

from environment.emr import init_db, get_triage_summary
from environment.sensors import get_scenario
from protocols.messages import make_register_msg

from agents.triage_agent import TriageAgent
from agents.resource_agent import ResourceAgent
from agents.notification_agent import NotificationAgent
from agents.monitor_agent import MonitorAgent

XMPP_SERVER = "localhost"
PASSWORD     = "triage123"

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║      SMART HOSPITAL TRIAGE AGENT SYSTEM                     ║
║      DCIT 403 — Intelligent Agent Systems — KNUST           ║
║      Designed using Prometheus AOSE Methodology             ║
╚══════════════════════════════════════════════════════════════╝"""

SEP = "─" * 64


# ── Controller Agent ─────────────────────────────────────────────
# Sends patient scenarios to the TriageAgent then prints the summary.
# Messages MUST be sent from inside a Behaviour — not from main().
class ControllerAgent(Agent):

    class RunDemoBehaviour(OneShotBehaviour):
        async def run(self):
            await asyncio.sleep(2)      # wait for all agents to settle

            print(f"\n{SEP}")
            print("[Demo] All 4 agents online. Sending patient scenarios...")
            print(f"{SEP}\n")

            for pid in ["P001", "P002", "P003", "P004", "P005"]:
                print(f"[Controller] ─── Registering patient {pid} ───")
                vitals = get_scenario(pid)
                msg = make_register_msg(vitals)
                await self.send(msg)
                await asyncio.sleep(4)  # let agents process each patient

            print(f"\n{SEP}")
            print("[Demo] MonitorAgent running periodic check (every 8s)...")
            print("[Demo] P002 SpO2=89% will trigger DETERIORATION_ALERT...")
            print(f"{SEP}")
            await asyncio.sleep(12)     # MonitorAgent fires here

            # ── Final summary ─────────────────────────────────────
            print(f"\n{SEP}")
            print("FINAL TRIAGE SUMMARY — EMR LOG")
            print(f"{SEP}")

            esi_col = {1:"\033[91m",2:"\033[31m",3:"\033[33m",
                       4:"\033[32m",5:"\033[37m"}
            rst = "\033[0m"
            rows = get_triage_summary()
            if rows:
                print(f"{'Patient':<10} {'ESI':<6} {'Ward':<10} {'Bed':<12} Escalated")
                print("─" * 52)
                for row in rows:
                    pid, esi, ward, bed, ts, esc = row
                    c = esi_col.get(esi, "")
                    e = f"\033[91mYES ⚠{rst}" if esc else "No"
                    print(f"{pid:<10} {c}ESI-{esi}{rst}      "
                          f"{str(ward):<10} {str(bed):<12} {e}")
            else:
                print("  (No records yet)")

            print(f"\n{SEP}")
            print("Prometheus artifacts demonstrated:")
            print("  ✓ Phase 1 — Percepts (vitals) + Actions (bed alloc, alerts)")
            print("  ✓ Phase 2 — 4 agents communicating via FIPA-ACL messages")
            print("  ✓ Phase 2 — Acquaintance: Triage↔Resource↔Monitor↔Notif")
            print("  ✓ Phase 3 — Percept→Decide→Act loop in TriageAgent output")
            print("  ✓ Phase 3 — Belief revision via MonitorAgent deterioration")
            print(f"{SEP}\n")

            # Signal done
            await self.agent.stop()

    async def setup(self):
        self.add_behaviour(self.RunDemoBehaviour())


# ── Main ─────────────────────────────────────────────────────────
async def main():
    print(BANNER)
    print(f"\n{SEP}")
    print("[Setup] Initialising EMR database...")
    init_db()
    print("[Setup] Starting agents...\n")

    resource_agent     = ResourceAgent    (f"resource@{XMPP_SERVER}",     PASSWORD)
    notification_agent = NotificationAgent(f"notification@{XMPP_SERVER}", PASSWORD)
    monitor_agent      = MonitorAgent     (f"monitor@{XMPP_SERVER}",      PASSWORD)
    triage_agent       = TriageAgent      (f"triage@{XMPP_SERVER}",       PASSWORD)
    controller_agent   = ControllerAgent  (f"controller@{XMPP_SERVER}",   PASSWORD)

    await resource_agent.start(auto_register=True)
    await notification_agent.start(auto_register=True)
    await monitor_agent.start(auto_register=True)
    await triage_agent.start(auto_register=True)
    await controller_agent.start(auto_register=True)

    # Wait until the controller finishes its demo behaviour
    await spade.wait_until_finished(controller_agent)

    await triage_agent.stop()
    await resource_agent.stop()
    await notification_agent.stop()
    await monitor_agent.stop()


if __name__ == "__main__":
    spade.run(main(), embedded_xmpp_server=True)
