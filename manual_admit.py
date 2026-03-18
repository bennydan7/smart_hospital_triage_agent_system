"""
manual_admit.py — Manual Patient Admission for Smart Hospital Triage Agent System
Run with: python3 manual_admit.py
"""
import sys, os
from logging_config import get_logger
sys.path.insert(0, os.path.dirname(__file__))

import asyncio
import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour

from environment.sensors import get_scenario
from protocols.messages import make_register_msg
from beliefs.data import PatientVitals
import time

XMPP_SERVER = "localhost"
PASSWORD     = "triage123"

SEP = "─" * 64

class ManualAdmitAgent(Agent):
    logger = get_logger("ManualAdmitAgent")
    class ManualAdmitBehaviour(OneShotBehaviour):
        async def run(self):
            self.agent.logger.info(f"\n{SEP}")
            self.agent.logger.info("[Manual] Manual patient admission mode.")
            self.agent.logger.info(f"{SEP}\n")
            try:
                batch_count = input("How many patients do you want to admit? (default 1): ").strip()
                batch_count = int(batch_count) if batch_count.isdigit() and int(batch_count) > 0 else 1
            except Exception:
                batch_count = 1
            for i in range(batch_count):
                print(f"\n--- Patient {i+1} ---")
                pid = input("Enter patient ID (or 'exit'): ").strip()
                if pid.lower() == 'exit':
                    break
                heart_rate = input("  Heart rate (bpm): ").strip()
                spo2 = input("  SpO2 (%): ").strip()
                systolic_bp = input("  Systolic BP (mmHg): ").strip()
                respiratory_rate = input("  Respiratory rate (bpm): ").strip()
                temperature = input("  Temperature (C): ").strip()
                chief_complaint = input("  Chief complaint: ").strip()
                try:
                    vitals = PatientVitals(
                        patient_id=pid,
                        heart_rate=int(heart_rate),
                        spo2=int(spo2),
                        systolic_bp=int(systolic_bp),
                        respiratory_rate=int(respiratory_rate),
                        temperature=float(temperature),
                        chief_complaint=chief_complaint,
                        arrival_time=time.time()
                    )
                except Exception as e:
                    self.agent.logger.error(f"[Error] Invalid input: {e}")
                    continue
                msg = make_register_msg(vitals)
                await self.send(msg)
                self.agent.logger.info(f"[Manual] Patient {pid} admitted.")
                await asyncio.sleep(2)
            self.agent.logger.info(f"\n{SEP}")
            self.agent.logger.info("[Manual] Manual admission session ended.")
            self.agent.logger.info(f"{SEP}\n")
            await self.agent.stop()
    async def setup(self):
        self.add_behaviour(self.ManualAdmitBehaviour())

async def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║      SMART HOSPITAL TRIAGE AGENT SYSTEM                     ║
║      DCIT 403 — Intelligent Agent Systems — KNUST           ║
║      Designed using Prometheus AOSE Methodology             ║
╚══════════════════════════════════════════════════════════════╝""")
    print(f"\n{SEP}")
    print("[Setup] Initialising EMR database...")
    from environment.emr import init_db, get_triage_summary
    init_db()
    print("[Setup] Starting agents...\n")

    from agents.triage_agent import TriageAgent
    from agents.resource_agent import ResourceAgent
    from agents.notification_agent import NotificationAgent
    from agents.monitor_agent import MonitorAgent

    resource_agent     = ResourceAgent    (f"resource@{XMPP_SERVER}",     PASSWORD)
    notification_agent = NotificationAgent(f"notification@{XMPP_SERVER}", PASSWORD)
    monitor_agent      = MonitorAgent     (f"monitor@{XMPP_SERVER}",      PASSWORD)
    triage_agent       = TriageAgent      (f"triage@{XMPP_SERVER}",       PASSWORD)
    manual_agent       = ManualAdmitAgent (f"controller@{XMPP_SERVER}",   PASSWORD)

    await resource_agent.start(auto_register=True)
    await notification_agent.start(auto_register=True)
    await monitor_agent.start(auto_register=True)
    await triage_agent.start(auto_register=True)
    await manual_agent.start(auto_register=True)

    await spade.wait_until_finished(manual_agent)

    await triage_agent.stop()
    await resource_agent.stop()
    await notification_agent.stop()
    await monitor_agent.stop()

    # Print triage summary
    print(f"\n{SEP}")
    print("FINAL TRIAGE SUMMARY — EMR LOG")
    print(f"{SEP}")
    esi_col = {1:"\033[91m",2:"\033[31m",3:"\033[33m",4:"\033[32m",5:"\033[37m"}
    rst = "\033[0m"
    rows = get_triage_summary()
    if rows:
        print(f"{'Patient':<10} {'ESI':<6} {'Ward':<10} {'Bed':<12} Escalated")
        print("─" * 52)
        for row in rows:
            pid, esi, ward, bed, ts, esc = row
            c = esi_col.get(esi, "")
            e = f"\033[91mYES ⚠{rst}" if esc else "No"
            print(f"{pid:<10} {c}ESI-{esi}{rst}      {str(ward):<10} {str(bed):<12} {e}")
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

if __name__ == "__main__":
    spade.run(main(), embedded_xmpp_server=True)
