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
            while True:
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
    logger = get_logger("ManualAdmit")
    logger.info(f"\n{SEP}")
    logger.info("[Setup] Starting ManualAdmitAgent...")
    agent = ManualAdmitAgent(f"controller@{XMPP_SERVER}", PASSWORD)
    await agent.start(auto_register=True)
    await spade.wait_until_finished(agent)
    await agent.stop()

if __name__ == "__main__":
    spade.run(main(), embedded_xmpp_server=False)
