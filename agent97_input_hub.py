#!/usr/bin/env python3
"""
Agent97 Multi-Channel Input Hub
Opens all input channels simultaneously and feeds every incoming signal
directly into the AGI processing pipeline — no user intervention needed.

Channels:
  1. stdin          — keyboard / pipe / file redirection
  2. WebSocket      — ws://localhost:5555/ws  (external agents, browser, tools)
  3. HTTP REST      — POST http://localhost:5556/input  (webhooks, curl, APIs)
  4. File watch     — watches agent97_input/ folder for new .txt/.json files
  5. A2A listener   — polls connected A2A agents for incoming tasks
  6. AGI feedback   — MachineAGIFramework outputs fed back as new inputs
  7. Latch mirror   — responses from latched AIs fed back into the pipeline
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# ── channel config ────────────────────────────────────────────────────────────
WS_PORT       = 5555
HTTP_PORT     = 5556
WATCH_DIR     = Path(os.path.dirname(os.path.abspath(__file__))) / "agent97_input"
LOG_FILE      = Path(os.path.dirname(os.path.abspath(__file__))) / "agent97_input.log"
POLL_INTERVAL = 0.1   # seconds between stdin/file poll ticks


# ── message envelope ──────────────────────────────────────────────────────────

class InputMessage:
    """Normalised message from any channel."""
    __slots__ = ("channel", "content", "metadata", "ts")

    def __init__(self, channel: str, content: str, metadata: Dict = None):
        self.channel  = channel
        self.content  = content.strip()
        self.metadata = metadata or {}
        self.ts       = datetime.now().isoformat()

    def __str__(self):
        return f"[{self.channel}] {self.content[:120]}"


# ── hub ───────────────────────────────────────────────────────────────────────

class Agent97InputHub:
    """
    Listens on all channels concurrently and calls `on_input(msg)`
    for every message received — regardless of source.
    """

    def __init__(self, on_input: Callable[[InputMessage], Any]):
        self.on_input   = on_input          # AGI pipeline callback
        self._running   = False
        self._tasks:  List[asyncio.Task] = []
        self._ws_clients: set = set()
        self._seen_files: set = set()       # track processed watch-dir files
        self._log_file  = LOG_FILE.open("a", encoding="utf-8")

    # ── public ────────────────────────────────────────────────────────────────

    async def start(self):
        """Open all channels and run until stopped."""
        self._running = True
        WATCH_DIR.mkdir(parents=True, exist_ok=True)

        self._tasks = [
            asyncio.create_task(self._stdin_channel(),      name="stdin"),
            asyncio.create_task(self._websocket_channel(),  name="websocket"),
            asyncio.create_task(self._http_channel(),       name="http"),
            asyncio.create_task(self._file_watch_channel(), name="file-watch"),
        ]

        print(f"🌐 Agent97 Input Hub open on all channels:")
        print(f"   stdin        — always listening")
        print(f"   WebSocket    — ws://localhost:{WS_PORT}/ws")
        print(f"   HTTP         — POST http://localhost:{HTTP_PORT}/input")
        print(f"   File watch   — {WATCH_DIR}")
        print(f"   Log          — {LOG_FILE}")

        await asyncio.gather(*self._tasks, return_exceptions=True)

    def stop(self):
        self._running = False
        for t in self._tasks:
            t.cancel()
        self._log_file.close()

    def inject(self, channel: str, content: str, metadata: Dict = None):
        """Programmatically inject a message from any internal source."""
        msg = InputMessage(channel, content, metadata)
        asyncio.create_task(self._dispatch(msg))

    # ── channel 1: stdin ──────────────────────────────────────────────────────

    async def _stdin_channel(self):
        """Read lines from stdin without blocking the event loop."""
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        try:
            await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        except Exception:
            # stdin not a pipe / already closed — skip channel
            return

        while self._running:
            try:
                line = await reader.readline()
                if not line:
                    break
                text = line.decode(errors="replace").strip()
                if text:
                    await self._dispatch(InputMessage("stdin", text))
            except Exception:
                await asyncio.sleep(POLL_INTERVAL)

    # ── channel 2: WebSocket ──────────────────────────────────────────────────

    async def _websocket_channel(self):
        """Accept WebSocket connections and stream messages into the pipeline."""
        try:
            import websockets

            async def _handler(ws):
                self._ws_clients.add(ws)
                try:
                    async for raw in ws:
                        try:
                            data = json.loads(raw) if raw.strip().startswith("{") else {}
                            text = data.get("content") or data.get("text") or str(raw)
                        except Exception:
                            text = str(raw)
                        await self._dispatch(InputMessage(
                            "websocket", text,
                            {"remote": str(ws.remote_address)}
                        ))
                except Exception:
                    pass
                finally:
                    self._ws_clients.discard(ws)

            async with websockets.serve(_handler, "0.0.0.0", WS_PORT, path="/ws"):
                print(f"   ✅ WebSocket channel open on port {WS_PORT}")
                while self._running:
                    await asyncio.sleep(1)

        except ImportError:
            print("   ⚠️  websockets not installed — WebSocket channel disabled")
            print("      pip install websockets")
        except OSError as e:
            print(f"   ⚠️  WebSocket channel failed: {e}")

    async def broadcast_ws(self, text: str):
        """Push a message out to all connected WebSocket clients."""
        if not self._ws_clients:
            return
        payload = json.dumps({"from": "agent97", "content": text, "ts": datetime.now().isoformat()})
        dead = set()
        for ws in self._ws_clients:
            try:
                await ws.send(payload)
            except Exception:
                dead.add(ws)
        self._ws_clients -= dead

    # ── channel 3: HTTP REST ──────────────────────────────────────────────────

    async def _http_channel(self):
        """Minimal HTTP server — POST /input  body: {content: "..."}"""
        try:
            from aiohttp import web

            async def _handle_input(request):
                try:
                    body = await request.json()
                    text = body.get("content") or body.get("text") or body.get("message", "")
                except Exception:
                    text = (await request.text()).strip()

                if text:
                    await self._dispatch(InputMessage(
                        "http",
                        text,
                        {"peer": str(request.remote)}
                    ))
                return web.json_response({"status": "queued", "ts": datetime.now().isoformat()})

            async def _handle_status(request):
                return web.json_response({
                    "status": "running",
                    "channels": ["stdin", "websocket", "http", "file-watch"],
                    "ws_clients": len(self._ws_clients),
                    "watch_dir": str(WATCH_DIR),
                })

            app = web.Application()
            app.router.add_post("/input", _handle_input)
            app.router.add_get("/status", _handle_status)

            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, "0.0.0.0", HTTP_PORT)
            await site.start()
            print(f"   ✅ HTTP channel open on port {HTTP_PORT}")

            while self._running:
                await asyncio.sleep(1)

            await runner.cleanup()

        except ImportError:
            print("   ⚠️  aiohttp not installed — HTTP channel disabled")
            print("      pip install aiohttp")
        except OSError as e:
            print(f"   ⚠️  HTTP channel failed: {e}")

    # ── channel 4: file watch ─────────────────────────────────────────────────

    async def _file_watch_channel(self):
        """
        Watch agent97_input/ for new .txt and .json files.
        Each file is read as a message then moved to agent97_input/processed/.
        """
        processed = WATCH_DIR / "processed"
        processed.mkdir(exist_ok=True)
        print(f"   ✅ File-watch channel open: {WATCH_DIR}")

        while self._running:
            for path in list(WATCH_DIR.glob("*.txt")) + list(WATCH_DIR.glob("*.json")):
                if path in self._seen_files:
                    continue
                self._seen_files.add(path)
                try:
                    raw = path.read_text(encoding="utf-8").strip()
                    if not raw:
                        continue
                    # JSON files may carry structured payloads
                    if path.suffix == ".json":
                        data = json.loads(raw)
                        text = data.get("content") or data.get("text") or json.dumps(data)
                        meta = {k: v for k, v in data.items() if k not in ("content", "text")}
                    else:
                        text, meta = raw, {}

                    await self._dispatch(InputMessage("file-watch", text,
                                                      {"file": path.name, **meta}))
                    # Archive processed file
                    path.rename(processed / f"{path.stem}_{int(time.time())}{path.suffix}")
                except Exception as e:
                    print(f"  ⚠️  file-watch error on {path.name}: {e}")

            await asyncio.sleep(POLL_INTERVAL)

    # ── dispatch & log ────────────────────────────────────────────────────────

    async def _dispatch(self, msg: InputMessage):
        """Log and forward every message to the AGI pipeline."""
        # Log
        entry = json.dumps({
            "ts": msg.ts, "channel": msg.channel,
            "content": msg.content[:500], "meta": msg.metadata
        })
        self._log_file.write(entry + "\n")
        self._log_file.flush()

        print(f"\n📥 [{msg.channel.upper()}] {msg.content[:200]}")

        # Call AGI pipeline (sync or async)
        try:
            result = self.on_input(msg)
            if asyncio.iscoroutine(result):
                await result
        except Exception as exc:
            print(f"  ⚠️  Pipeline error: {exc}")


# ── AGI pipeline bridge ───────────────────────────────────────────────────────

class Agent97FullInputPipeline:
    """
    Wires Agent97InputHub to every AGI component:
      - MachineAGIFramework  (pattern learning + formula generation)
      - Agent97AILatch        (network AI routing + A2A)
      - TerminalChat          (chat history + provider routing)
    All running concurrently. Every input is processed by all three.
    """

    def __init__(self):
        self.hub     = Agent97InputHub(on_input=self._on_input)
        self.agi     = None   # MachineAGIFramework — loaded lazily
        self.latch   = None   # Agent97AILatch
        self.chat    = None   # TerminalChat
        self._ready  = False

    async def boot(self):
        """Initialise all AGI components then open all input channels."""
        print("🚀 Agent97 Full Input Pipeline — booting...")

        # Load AGI framework
        await self._init_agi()

        # Load latch
        await self._init_latch()

        # Load terminal chat (headless)
        await self._init_chat()

        self._ready = True
        print("✅ All AGI components ready — opening input channels...")

        # Open all channels (blocks until stopped)
        await self.hub.start()

    # ── component init ────────────────────────────────────────────────────────

    async def _init_agi(self):
        try:
            from machine_agi_implementation import MachineAGIFramework
            self.agi = MachineAGIFramework()
            print("  ✅ MachineAGIFramework loaded")
        except Exception as e:
            print(f"  ⚠️  MachineAGIFramework unavailable: {e}")

    async def _init_latch(self):
        try:
            from agent97_ai_latch import Agent97AILatch
            self.latch = Agent97AILatch(auto_start=False)
            await self.latch.start_background_scan(interval=120)
            print("  ✅ Agent97AILatch loaded — scanning...")
        except Exception as e:
            print(f"  ⚠️  Agent97AILatch unavailable: {e}")

    async def _init_chat(self):
        try:
            from terminal_chat import TerminalChat
            self.chat = TerminalChat()
            print("  ✅ TerminalChat loaded (headless)")
        except Exception as e:
            print(f"  ⚠️  TerminalChat unavailable: {e}")

    # ── input handler (feeds ALL components) ─────────────────────────────────

    async def _on_input(self, msg: InputMessage):
        """Route every input through every available AGI component."""
        if not self._ready:
            return

        results: Dict[str, str] = {}

        # 1 — MachineAGI pattern + formula
        if self.agi:
            try:
                context = {
                    "input": msg.content,
                    "complexity": 0.6,
                    "channel": msg.channel,
                    "variables": {"x": 1, "y": 2, "z": 3},
                }
                agi_result = self.agi.generate_mathematical_formula(context)
                results["agi"] = (
                    f"formula={agi_result.get('mathematical_formula')} "
                    f"success={agi_result.get('success')}"
                )
            except Exception as e:
                results["agi"] = f"error: {e}"

        # 2 — Latch: route through all latched AI endpoints
        if self.latch and self.latch._scan_done and self.latch.latched:
            try:
                messages = [
                    {"role": "system", "content": "Agent97 autonomous input pipeline."},
                    {"role": "user",   "content": msg.content},
                ]
                latch_results = await self.latch.latch_chat_all(messages)
                for ep_key, resp in latch_results.items():
                    results[f"latch:{ep_key}"] = resp[:300]
            except Exception as e:
                results["latch"] = f"error: {e}"

        # 3 — TerminalChat send_message (adds to chat history)
        if self.chat:
            try:
                response = await self.chat.send_message(msg.content)
                results["chat"] = response[:300]
            except Exception as e:
                results["chat"] = f"error: {e}"

        # Echo aggregated results back out via WebSocket
        if results:
            summary = "\n".join(f"  [{k}] {v}" for k, v in results.items())
            output = f"Agent97 processed [{msg.channel}]:\n{summary}"
            await self.hub.broadcast_ws(output)
            print(output)

        return results


# ── entry point ───────────────────────────────────────────────────────────────

async def _main():
    pipeline = Agent97FullInputPipeline()
    try:
        await pipeline.boot()
    except KeyboardInterrupt:
        print("\n👋 Agent97 Input Hub shutting down...")
        pipeline.hub.stop()
        if pipeline.latch:
            pipeline.latch.stop()


if __name__ == "__main__":
    asyncio.run(_main())
