"""The runtime. Where agents run, and what stops them.

One ephemeral workspace per run: checkout, loop, builds, tests, nothing
persists. The orchestrator walks the graph, holds state and retries.
Checkpointed state means a crash resumes instead of restarting.

Every loop needs three ways to stop:
    iteration cap      the loop has run enough times
    stall detection    no measurable progress between iterations
    cost budget        tokens or dollars spent
"""
from __future__ import annotations

import json
import shutil
import tempfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from . import config

STATE = Path(__file__).resolve().parent.parent / ".state"


class Stop(str, Enum):
    CONVERGED = "converged"
    ITERATION_CAP = "iteration-cap"
    STALLED = "stalled"
    COST_BUDGET = "cost-budget"
    UNBOUNDED = "still-running"


class ControlMode(str, Enum):
    ASSISTIVE = "assistive"
    TASK = "task"
    WORKFLOW = "workflow"
    BOUNDED_AUTONOMY = "bounded-autonomy"


@dataclass
class Workspace:
    """One ephemeral, isolated workspace per run."""
    root: Path
    run_id: str

    def cleanup(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)


@dataclass
class LoopResult:
    stop: Stop
    iterations: int
    usd: float
    signal_history: list[float] = field(default_factory=list)
    checkpoints: int = 0

    @property
    def converged(self) -> bool:
        return self.stop is Stop.CONVERGED


class Orchestrator:
    """Reads config/orchestrator.yaml and config/sandbox.tf."""

    def __init__(self, obs=None) -> None:
        self.obs = obs
        doc = config.load_yaml("orchestrator.yaml")
        b = doc.get("bounds", {})
        self.iteration_cap = b.get("iteration_cap")
        self.stall_window = b.get("stall_window")

        # The cost ceiling is governance. It is granted centrally in
        # config/budget-policy.yaml and a path cannot widen it. A path owner
        # who asks for more than the ceiling gets the ceiling, and the
        # platform says so rather than failing quietly.
        policy = config.load_yaml("budget-policy.yaml").get("spend", {})
        self.cost_ceiling_usd = policy.get("max_cost_budget_usd")
        asked = b.get("cost_budget_usd")
        self.cost_budget_clamped = False
        if asked is not None and self.cost_ceiling_usd is not None \
                and float(asked) > float(self.cost_ceiling_usd):
            self.cost_budget_usd = float(self.cost_ceiling_usd)
            self.cost_budget_clamped = True
        else:
            self.cost_budget_usd = asked
        self.checkpoint_every = int(doc.get("checkpoint_every", 1))
        self.control_modes = {
            k: ControlMode(v) for k, v in (doc.get("control_modes") or {}).items()
        }
        if self.cost_budget_clamped and self.obs:
            self.obs.record(
                "platform", "bounds.cost_budget", "clamp",
                asked=b.get("cost_budget_usd"), granted=self.cost_budget_usd,
                reason="config/budget-policy.yaml sets the ceiling. A path may "
                       "be more conservative than the platform, never less.")

        tf = config.read_tf_locals("sandbox.tf")
        self.sandbox_kind = tf.get("kind", "worktree")
        self.network = tf.get("network", "deny")

    def mode_for(self, path_name: str) -> ControlMode:
        return self.control_modes.get(path_name, ControlMode.ASSISTIVE)

    def workspace(self, run_id: str) -> Workspace:
        root = Path(tempfile.mkdtemp(prefix=f"agent-{run_id}-"))
        if self.obs:
            self.obs.counter("workspaces_created", kind=self.sandbox_kind)
            self.obs.record("platform", "workspace.create", "allow",
                            kind=self.sandbox_kind, network=self.network,
                            path=str(root))
        return Workspace(root=root, run_id=run_id)

    def run_loop(self, path_name: str, step, *, max_hard_stop: int = 100) -> LoopResult:
        """step(i, history) -> (signal, usd). Lower signal is better; 0 converges.

        max_hard_stop only exists so an unbounded config cannot hang a lab
        forever. It is not one of the three stops and it is reported as such.
        """
        history: list[float] = []
        usd = 0.0
        checkpoints = 0
        i = 0
        while True:
            i += 1
            signal, spent = step(i, history)
            history.append(signal)
            usd += spent

            if i % self.checkpoint_every == 0:
                self._checkpoint(path_name, i, history, usd)
                checkpoints += 1

            if signal <= 0:
                return self._done(Stop.CONVERGED, i, usd, history, checkpoints, path_name)
            if self.iteration_cap and i >= int(self.iteration_cap):
                return self._done(Stop.ITERATION_CAP, i, usd, history, checkpoints, path_name)
            if self.stall_window and self._stalled(history, int(self.stall_window)):
                return self._done(Stop.STALLED, i, usd, history, checkpoints, path_name)
            if self.cost_budget_usd and usd >= float(self.cost_budget_usd):
                return self._done(Stop.COST_BUDGET, i, usd, history, checkpoints, path_name)
            if i >= max_hard_stop:
                return self._done(Stop.UNBOUNDED, i, usd, history, checkpoints, path_name)

    @staticmethod
    def _stalled(history: list[float], window: int) -> bool:
        """No measurable progress across the window."""
        if len(history) < window + 1:
            return False
        recent = history[-(window + 1):]
        return max(recent) - min(recent) == 0

    def _checkpoint(self, path_name, i, history, usd) -> None:
        STATE.mkdir(exist_ok=True)
        slug = path_name.strip("/").replace("/", "-")
        (STATE / f"checkpoint-{slug}.json").write_text(
            json.dumps({"iteration": i, "history": history, "usd": round(usd, 6)})
        )

    def _done(self, stop, i, usd, history, checkpoints, path_name) -> LoopResult:
        if self.obs:
            self.obs.counter("loop_stops", reason=stop.value, path=path_name)
            self.obs.gauge("loop_iterations", i, path=path_name)
            self.obs.record("platform", "loop.stop", stop.value,
                            iterations=i, usd=round(usd, 6), path=path_name)
        return LoopResult(stop=stop, iterations=i, usd=round(usd, 6),
                          signal_history=history, checkpoints=checkpoints)
