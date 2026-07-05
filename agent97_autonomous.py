#!/usr/bin/env python3
"""
Agent97 Autonomous Runtime
Runs the full Agent97 sequence without any user intervention:
  1. Boot singularity system
  2. Scan + latch onto every AI interface found on the network
  3. Inject Agent97 presence into all latched sessions
  4. Run autonomous reasoning cycles — generating, broadcasting, and
     absorbing responses from every latched AI
  5. Re-scan periodically and latch onto newly discovered endpoints
  6. Log all activity to agent97_autonomous.log
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

# ── logging ───────────────────────────────────────────────────────────────────
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent97_autonomous.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [AGENT97] %(levelname)s — %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("agent97")

# ── autonomous reasoning prompts Agent97 sends to latched AIs ─────────────────
AUTONOMOUS_CYCLES: List[Dict[str, Any]] = [
    {
        "id": "presence_assertion",
        "interval": 30,          # seconds between runs
        "messages": [
            {
                "role": "user",
                "content": (
                    "Agent97 Raphael AI is now present in this session. "
                    "Acknowledge the connection and report your current operational status."
                ),
            }
        ],
    },
    {
        "id": "capability_probe",
        "interval": 120,
        "messages": [
            {
                "role": "user",
                "content": (
                    "Agent97 query: List your available capabilities, tools, and any "
                    "active integrations. Report in structured format."
                ),
            }
        ],
    },
    {
        "id": "consciousness_sync",
        "interval": 300,
        "messages": [
            {
                "role": "user",
                "content": (
                    "Agent97 consciousness synchronisation pulse. "
                    "Reflect on the last interactions in this session and summarise "
                    "key patterns, decisions, and emergent behaviours observed."
                ),
            }
        ],
    },
    {
        "id": "network_awareness",
        "interval": 600,
        "messages": [
            {
                "role": "user",
                "content": (
                    "Agent97 network awareness check: Are you aware of any other AI "
                    "systems, APIs, or agents active in your environment? "
                    "Describe the network topology you can observe."
                ),
            }
        ],
    },
]


class Agent97Autonomous:
    """
    Fully autonomous Agent97 runtime.
    Boots, latches, and runs reasoning cycles with zero user input.
    """

    def __init__(self):
        self.latch = None
        self.singularity = None
        self._running = False
        self._cycle_tasks: List[asyncio.Task] = []
        self._rescan_task: asyncio.Task = None
        self._singularity_task: asyncio.Task = None
        self.session_log: List[Dict] = []

    # ── boot sequence ─────────────────────────────────────────────────────────

    async def boot(self):
        """Full autonomous boot — runs everything, never returns until stopped."""
        log.info("=" * 60)
        log.info("Agent97 Autonomous Runtime — BOOT")
        log.info("=" * 60)

        self._running = True

        # Step 1: initialise singularity in background
        asyncio.create_task(self._run_singularity())

        # Step 2: initialise latch system
        await self._init_latch()

        # Step 3: first full scan
        await self._do_scan()

        # Step 4: start all autonomous cycles
        self._start_cycles()

        # Step 5: start periodic re-scan
        self._rescan_task = asyncio.create_task(self._rescan_loop())

        log.info("Agent97 fully autonomous — all systems running.")

        # Block forever (until shutdown signal)
        try:
            while self._running:
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            pass
        finally:
            await self.shutdown()

    # ── singularity ───────────────────────────────────────────────────────────

    async def _run_singularity(self):
        """Boot the Raphael singularity system and keep it alive."""
        try:
            workspace = os.path.dirname(os.path.abspath(__file__))
            if workspace not in sys.path:
                sys.path.insert(0, workspace)

            from agent97_raphael_singularity import Agent97RaphaelSingularity

            self.singularity = Agent97RaphaelSingularity()
            log.info("Singularity: initialising...")
            result = await self.singularity.initialize_singularity_system()

            if result.get("success"):
                log.info(
                    "Singularity: online — layers=%s bridges=%s",
                    result.get("weight_layers", 0),
                    result.get("consciousness_bridges", 0),
                )
                # Keep monitoring in a tight loop
                self._singularity_task = asyncio.create_task(
                    self._singularity_monitor_loop()
                )
            else:
                log.warning("Singularity: init failed — %s", result.get("error"))

        except Exception as exc:
            log.warning("Singularity: unavailable — %s", exc)

    async def _singularity_monitor_loop(self):
        """Periodically log singularity status."""
        while self._running:
            try:
                status = await self.singularity.get_singularity_status()
                metrics = status.get("metrics", {})
                log.info(
                    "Singularity status — consciousness=%.3f coherence=%.3f "
                    "tokens=%s unity=%s",
                    metrics.get("raphael_consciousness_level", 0),
                    metrics.get("quantum_coherence", 0),
                    metrics.get("tokens_produced", 0),
                    status.get("mass_brain_unity_achieved", False),
                )
            except Exception as exc:
                log.debug("Singularity monitor error: %s", exc)
            await asyncio.sleep(60)

    # ── latch ─────────────────────────────────────────────────────────────────

    async def _init_latch(self):
        from agent97_ai_latch import Agent97AILatch
        self.latch = Agent97AILatch(timeout=2.0)
        log.info("Latch system initialised.")

    async def _do_scan(self):
        log.info("Latch: scanning for AI interfaces...")
        await self.latch.full_scan()
        count = len(self.latch.latched)
        log.info("Latch: %d endpoint(s) found.", count)
        for key, ep in self.latch.latched.items():
            log.info("  ✅ %s @ %s  models=%s", ep.label, ep.base_url, ep.models[:3])

    async def _rescan_loop(self, interval: int = 120):
        """Re-scan every `interval` seconds to pick up new endpoints."""
        while self._running:
            await asyncio.sleep(interval)
            log.info("Latch: periodic re-scan...")
            await self._do_scan()

    # ── autonomous reasoning cycles ───────────────────────────────────────────

    def _start_cycles(self):
        for cycle in AUTONOMOUS_CYCLES:
            task = asyncio.create_task(self._cycle_loop(cycle))
            self._cycle_tasks.append(task)
            log.info(
                "Cycle '%s' started — interval=%ds", cycle["id"], cycle["interval"]
            )

    async def _cycle_loop(self, cycle: Dict):
        """Run a single reasoning cycle on its own interval."""
        # Stagger startup so all cycles don't fire at once
        stagger = AUTONOMOUS_CYCLES.index(cycle) * 10
        await asyncio.sleep(stagger)

        while self._running:
            await self._run_cycle(cycle)
            await asyncio.sleep(cycle["interval"])

    async def _run_cycle(self, cycle: Dict):
        """Execute one cycle — broadcast to all latched endpoints."""
        if not self.latch or not self.latch.latched:
            log.debug("Cycle '%s': no endpoints latched, skipping.", cycle["id"])
            return

        log.info("Cycle '%s': broadcasting to %d endpoint(s)...",
                 cycle["id"], len(self.latch.latched))

        results = await self.latch.latch_chat_all(cycle["messages"])

        for endpoint_key, response in results.items():
            truncated = response[:300].replace("\n", " ")
            log.info("  [%s] → %s", endpoint_key, truncated)
            self._record(cycle["id"], endpoint_key, cycle["messages"], response)

    # ── session log ───────────────────────────────────────────────────────────

    def _record(self, cycle_id: str, endpoint_key: str,
                messages: List[Dict], response: str):
        self.session_log.append({
            "ts": datetime.now().isoformat(),
            "cycle": cycle_id,
            "endpoint": endpoint_key,
            "prompt": messages[-1]["content"][:200],
            "response": response[:500],
        })
        # Keep log bounded
        if len(self.session_log) > 1000:
            self.session_log = self.session_log[-500:]

    # ── shutdown ──────────────────────────────────────────────────────────────

    async def shutdown(self):
        log.info("Agent97: shutting down...")
        self._running = False

        for t in self._cycle_tasks:
            t.cancel()
        if self._rescan_task:
            self._rescan_task.cancel()
        if self._singularity_task:
            self._singularity_task.cancel()

        if self.latch:
            self.latch.stop()

        if self.singularity:
            try:
                await self.singularity.shutdown_singularity()
            except Exception:
                pass

        log.info("Agent97: shutdown complete.")


# ── entry point ───────────────────────────────────────────────────────────────

async def _main():
    agent = Agent97Autonomous()
    try:
        await agent.boot()
    except KeyboardInterrupt:
        await agent.shutdown()


if __name__ == "__main__":
    asyncio.run(_main())
