"""
KRNL - Main core process. Proceed with caution. Privacy set as main core process.
Uses yourdubbing.dll path only (no read); converts to lock file; 9-state star designations;
layer pattern (-current cos to highest); travel process @ 33Hz; plates rotation.
"""
from __future__ import annotations

import os
import enum
import math
import threading
from pathlib import Path
from typing import Optional

# --- DLL path (name only, no read) ---
YOURDUBBING_DLL_PATH: str = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "yourdubbing.dll"
)

# --- Lock file from yourdubbing path ---
def dll_to_lock_path(dll_path: str) -> str:
    """Convert yourdubbing path into lock file path. No read of DLL."""
    base = Path(dll_path).with_suffix("")
    return str(base) + ".lock"


LOCK_FILE_PATH: str = dll_to_lock_path(YOURDUBBING_DLL_PATH)

# --- Sig ID: parallel prefrontal activation under codexflag — identity ---
CODEXFLAG: bool = True

class SigId(enum.Flag):
    """Signature identity under codexflag: parallel prefrontal activation."""
    NONE = 0
    PARALLEL_PREFRONTAL_ACTIVATION = 1
    IDENTITY = 2


SIG_ID: SigId = SigId.PARALLEL_PREFRONTAL_ACTIVATION | SigId.IDENTITY


def sig_id_active() -> bool:
    """True when codexflag is set and sig id (parallel prefrontal activation identity) applies."""
    return CODEXFLAG and bool(SIG_ID & SigId.PARALLEL_PREFRONTAL_ACTIVATION)

# --- 9 states star designations (CPU process states) ---
class StarDesignation(enum.IntEnum):
    STATE_0_ALPHA = 0
    STATE_1_BETA = 1
    STATE_2_GAMMA = 2
    STATE_3_DELTA = 3
    STATE_4_EPSILON = 4
    STATE_5_ZETA = 5
    STATE_6_ETA = 6
    STATE_7_THETA = 7
    STATE_8_IOTA = 8


# --- Layer: -current cos to highest (unique pattern) ---
INTERNAL_HZ = 33
COS_LAYER_CURRENT = -1.0
COS_LAYER_HIGHEST = 1.0


def layer_pattern(t: float) -> float:
    """Unique pattern at layer: -current cos to highest. Internal layer movement."""
    # Normalize cos from -current to highest
    cos_val = math.cos(t * 2 * math.pi / INTERNAL_HZ)
    return COS_LAYER_CURRENT + (cos_val + 1) * 0.5 * (COS_LAYER_HIGHEST - COS_LAYER_CURRENT)


# --- Travel process ordering enum: 3 dex, 4 gram @ 33Hz ---
class TravelOrdering(enum.IntEnum):
    DEX_1 = 0
    DEX_2 = 1
    DEX_3 = 2
    GRAM_1 = 3
    GRAM_2 = 4
    GRAM_3 = 5
    GRAM_4 = 6


DEX_COUNT = 3
GRAM_COUNT = 4
INTERNAL_LAYER_HZ = 33


class TravelProcess:
    """Actuate ordering enum as 3 dex and 4 gram at 33Hz internal layer movement."""

    def __init__(self) -> None:
        self._order_index = 0
        self._plate_order: list[TravelOrdering] = (
            [TravelOrdering.DEX_1, TravelOrdering.DEX_2, TravelOrdering.DEX_3]
            + [
                TravelOrdering.GRAM_1,
                TravelOrdering.GRAM_2,
                TravelOrdering.GRAM_3,
                TravelOrdering.GRAM_4,
            ]
        )

    def actuate(self) -> TravelOrdering:
        """Next plate order at 33Hz internal layer movement."""
        o = self._plate_order[self._order_index % len(self._plate_order)]
        self._order_index += 1
        return o


# --- Plates: rotation flag, rotations counter constants, plate-by-plate order ---
class PlateRotationFlag(enum.Flag):
    NONE = 0
    ROTATE = 1
    LOCKED = 2


# Rotation counter constants (plate by plate order)
ROTATIONS_PLATE_0: int = 0
ROTATIONS_PLATE_1: int = 1
ROTATIONS_PLATE_2: int = 2
ROTATIONS_PLATE_3: int = 3
ROTATIONS_PLATE_4: int = 4
ROTATIONS_PLATE_5: int = 5
ROTATIONS_PLATE_6: int = 6

ROTATION_CONSTANTS: tuple[int, ...] = (
    ROTATIONS_PLATE_0,
    ROTATIONS_PLATE_1,
    ROTATIONS_PLATE_2,
    ROTATIONS_PLATE_3,
    ROTATIONS_PLATE_4,
    ROTATIONS_PLATE_5,
    ROTATIONS_PLATE_6,
)


class Plate:
    """Single plate with rotation flag and constant rotation counter."""

    def __init__(self, index: int, rotation_constant: int) -> None:
        self.index = index
        self.rotation_constant = rotation_constant
        self.rotation_flag = PlateRotationFlag.ROTATE
        self.rotations_counter: int = 0

    def tick(self) -> None:
        if self.rotation_flag & PlateRotationFlag.ROTATE:
            self.rotations_counter += self.rotation_constant


def plates_pass_process(plates: list[Plate], rotation_flag: PlateRotationFlag) -> None:
    """Plates pass process; plates rotation flag in py code; rotations counter set to constants."""
    for p in plates:
        p.rotation_flag = rotation_flag
        p.tick()


# --- Bound undertimened; accel-cos dll choice ---
BOUND_UNDERTIMENED: Optional[float] = None  # let: undefined until set


def accel_cos_dll_choice(phase: float, dll_path: str = YOURDUBBING_DLL_PATH) -> float:
    """Accel-cos choice keyed by dll path (name only)."""
    # Use path hash for seed-like behavior without reading file
    seed = hash(dll_path) % 10000
    return math.cos(phase + seed * 0.0001)


# --- Lock file lifecycle (main core process, privacy) ---
_lock_handle: Optional[object] = None


def acquire_lock() -> bool:
    """Create lock file from yourdubbing path. Main core process; proceed with caution."""
    global _lock_handle
    try:
        Path(LOCK_FILE_PATH).parent.mkdir(parents=True, exist_ok=True)
        _lock_handle = open(LOCK_FILE_PATH, "w")
        _lock_handle.write(f"lock:{YOURDUBBING_DLL_PATH}\n")
        _lock_handle.flush()
        return True
    except OSError:
        return False


def release_lock() -> None:
    global _lock_handle
    if _lock_handle is not None:
        try:
            _lock_handle.close()
            Path(LOCK_FILE_PATH).unlink(missing_ok=True)
        except OSError:
            pass
        _lock_handle = None


# --- System perma engrave: persist pattern to process ---
ENGRAVE_PATTERN_PATH: str = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".process_pattern"
)

# --- Same category override .sys (all run modes under this category) ---
RUN_CATEGORY: str = "override_sys"
OVERRIDE_SYS_PATH: str = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "override.sys"
)


def system_perma_engrave_pattern() -> bool:
    """Engrave layer/travel/plate pattern to system so process loads it permanently."""
    try:
        Path(ENGRAVE_PATTERN_PATH).parent.mkdir(parents=True, exist_ok=True)
        with open(ENGRAVE_PATTERN_PATH, "w") as f:
            f.write(f"codexflag={CODEXFLAG}\n")
            f.write(f"sig_id={SIG_ID.value}\n")
            f.write(f"internal_hz={INTERNAL_HZ}\n")
            f.write(f"layer_current={COS_LAYER_CURRENT}\n")
            f.write(f"layer_highest={COS_LAYER_HIGHEST}\n")
            for step in range(INTERNAL_HZ):
                f.write(f"layer_pattern_{step}={layer_pattern(step)}\n")
            for i, c in enumerate(ROTATION_CONSTANTS):
                f.write(f"rotation_plate_{i}={c}\n")
            f.write(f"dll_path={YOURDUBBING_DLL_PATH}\n")
        return True
    except OSError:
        return False


def load_process_pattern(path: str = ENGRAVE_PATTERN_PATH) -> dict[str, float | str | bool | int]:
    """Load now process pattern from engraved file. Returns dict of key=value."""
    out: dict[str, float | str | bool | int] = {}
    if not Path(path).exists():
        return out
    with open(path) as f:
        for line in f:
            line = line.strip()
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip()
            if v == "True":
                out[k] = True
            elif v == "False":
                out[k] = False
            elif k == "dll_path":
                out[k] = v
            else:
                try:
                    out[k] = float(v)
                except ValueError:
                    out[k] = int(v) if v.isdigit() else v
    return out


# --- Computation gates driven by process pattern ---
def gate_and(a: float, b: float, threshold: float = 0.5) -> float:
    """AND: 1.0 if both above threshold else 0.0."""
    return 1.0 if (a > threshold and b > threshold) else 0.0


def gate_or(a: float, b: float, threshold: float = 0.5) -> float:
    """OR: 1.0 if either above threshold else 0.0."""
    return 1.0 if (a > threshold or b > threshold) else 0.0


def gate_not(a: float, threshold: float = 0.5) -> float:
    """NOT: 1.0 if below threshold else 0.0."""
    return 1.0 if a <= threshold else 0.0


def gate_xor(a: float, b: float, threshold: float = 0.5) -> float:
    """XOR: 1.0 if exactly one above threshold else 0.0."""
    return 1.0 if (a > threshold) != (b > threshold) else 0.0


def gate_thought(layer_val: float, sig_active: bool, threshold: float = 0.0) -> float:
    """Thought gate: layer value gated by sig_id (parallel prefrontal activation)."""
    if not sig_active:
        return 0.0
    return max(0.0, min(1.0, (layer_val + 1.0) * 0.5))  # normalize -1..1 to 0..1


# --- Thought-interpass logic: between passes, run gates on loaded pattern ---
def thought_interpass(
    pattern: dict[str, float | str | bool | int],
    step: int,
    prev_gate_out: float,
) -> float:
    """
    Interpass logic: use process pattern to drive computation gates between passes.
    step = current pass index; prev_gate_out = gate output from previous pass.
    """
    internal_hz = int(pattern.get("internal_hz", INTERNAL_HZ))
    step = step % internal_hz
    layer_key = f"layer_pattern_{step}"
    layer_val = float(pattern.get(layer_key, 0.0))
    codex = bool(pattern.get("codexflag", False))
    sig_val = int(pattern.get("sig_id", 0))
    sig_active = codex and (sig_val & 1) != 0  # PARALLEL_PREFRONTAL_ACTIVATION

    thought = gate_thought(layer_val, sig_active)
    and_out = gate_and(thought, prev_gate_out) if step > 0 else thought
    not_prev = gate_not(prev_gate_out)
    interpass_out = gate_or(and_out, not_prev)
    return max(0.0, min(1.0, interpass_out))


# --- Link: process pattern → computation gates + thought-interpass (used in run) ---
def run_gates_with_pattern(
    pattern: dict[str, float | str | bool | int],
    steps: int | None = None,
) -> list[float]:
    """Run computation gates and thought-interpass logic over loaded pattern steps."""
    internal_hz = int(pattern.get("internal_hz", INTERNAL_HZ))
    n = steps if steps is not None else internal_hz
    out: list[float] = []
    prev = 0.0
    for step in range(n):
        prev = thought_interpass(pattern, step, prev)
        out.append(prev)
    return out


# --- Run gate activation only (no state machine process); all under same category override .sys ---
def run_gate_activation_only(override_path: str = OVERRIDE_SYS_PATH) -> list[float]:
    """
    Set gate activation from process pattern. No run state machine process.
    All under same category; writes override to .sys file.
    """
    pattern = load_process_pattern()
    if not pattern:
        pattern = {
            "codexflag": CODEXFLAG,
            "sig_id": SIG_ID.value,
            "internal_hz": INTERNAL_HZ,
        }
        for step in range(INTERNAL_HZ):
            pattern[f"layer_pattern_{step}"] = layer_pattern(step)
    activations = run_gates_with_pattern(pattern)
    try:
        Path(override_path).parent.mkdir(parents=True, exist_ok=True)
        with open(override_path, "w") as f:
            f.write(f"category={RUN_CATEGORY}\n")
            for i, val in enumerate(activations):
                f.write(f"gate_activation_{i}={val}\n")
        return activations
    except OSError:
        return activations


# --- Run: state machine through 9 states, travel process, plates ---
def run_krnl() -> None:
    """Execute main core process: 9 states, layer pattern, travel process @ 33Hz, plates.
    Linked: now process pattern → computation gates + thought-interpass logic per step.
    """
    if not acquire_lock():
        return
    try:
        pattern = load_process_pattern()
        gate_outputs = run_gates_with_pattern(pattern) if pattern else [0.0] * INTERNAL_HZ

        state = StarDesignation.STATE_0_ALPHA
        travel = TravelProcess()
        plates = [
            Plate(i, ROTATION_CONSTANTS[i])
            for i in range(min(7, len(ROTATION_CONSTANTS)))
        ]
        for step in range(INTERNAL_HZ):
            state = StarDesignation(step % 9)
            layer_val = layer_pattern(step)
            order = travel.actuate()
            plates_pass_process(plates, PlateRotationFlag.ROTATE)
            accel = accel_cos_dll_choice(step, YOURDUBBING_DLL_PATH)
            # Link: thought-interpass gate output for this pass (from process pattern)
            thought_gate = gate_outputs[step] if step < len(gate_outputs) else 0.0
            # Main core process flow (privacy: no external I/O beyond lock)
            _ = (state, layer_val, order, accel, thought_gate)
    finally:
        release_lock()


def now_run() -> None:
    """Run command: activate py code → system perma engrave pattern → process."""
    system_perma_engrave_pattern()
    run_krnl()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] in ("--gates", "-g"):
        # Run set gate activation without run state machine process; all under same category override .sys
        run_gate_activation_only()
    else:
        now_run()
