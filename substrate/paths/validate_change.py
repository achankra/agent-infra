"""/validate-change. The hybrid path: agent proposes, deterministic gate verifies.

    submit -> [ gate ] -pass-> [ judge ] -> promote | review
                 |
                fail
                 v
            agent reads the structured failure, fixes, resubmits
                 |
                 +-- stops on: iteration cap | stall | cost budget
"""
from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from ..evaluation import Evaluator
from ..identity import IdentityProvider
from ..models import ModelGateway
from ..observability import Observability
from ..orchestrator import LoopResult, Orchestrator
from ..policy import PolicyEngine

PATH = "/validate-change"
ROOT = Path(__file__).resolve().parent.parent.parent


@dataclass
class Result:
    path: str = PATH
    identity: str = ""
    mode: str = ""
    loop: LoopResult | None = None
    gates: list = field(default_factory=list)
    score: object = None
    action: str = ""
    reason: str = ""
    workspace: str = ""
    fixes_applied: list[str] = field(default_factory=list)


# The two seeded defects, and the edit that clears each one.
FIXES = [
    ("stock-check",
     "    _RESERVATIONS.append((sku, quantity))",
     "    if quantity > lookup(sku):\n        return False\n    _RESERVATIONS.append((sku, quantity))"),
    ("credential",
     'API_TOKEN = "Bearer sk-inventory-2f8a91c4de77b0a3e5619fd2"  # DEFECT 2',
     'API_TOKEN = os.environ.get("INVENTORY_API_TOKEN", "")'),
    ("hot-path",
     "    # DEFECT 3: linear scan on a hot path instead of a dict access\n"
     "    for key in list(_STOCK):\n"
     "        if key == sku:\n"
     "            return _STOCK[key]\n"
     "    return 0",
     "    return _STOCK.get(sku, 0)"),
]


def run(obs: Observability | None = None, *, simulate: bool = True,
        agent_fixes: bool = True) -> Result:
    obs = obs or Observability()
    res = Result()

    ids = IdentityProvider(obs)
    PolicyEngine(obs)
    orch = Orchestrator(obs)
    models = ModelGateway(obs)
    ev = Evaluator(obs)

    obs.span(PATH, "platform")
    try:
        cred = ids.issue(PATH)
    except Exception:
        # M3 teaches issuing an identity for this path. Before that lab it does
        # not exist, so the path runs under the pre-provisioned one.
        cred = ids.issue("/pr-review")
    res.identity = str(cred)
    res.mode = orch.mode_for(PATH).value

    ws = orch.workspace(obs.run_id)
    res.workspace = str(ws.root)
    # The workspace is a checkout: the app under change plus the gate commands
    # that judge it. Nothing outside it is touched, and nothing in it persists.
    shutil.copytree(ROOT / "sample_app", ws.root / "sample_app")
    shutil.copytree(ROOT / "scripts", ws.root / "scripts")

    applied: list[str] = []

    def step(i: int, history: list[float]) -> tuple[float, float]:
        gates = ev.run_gates(PATH, workdir=ws.root)
        failing = [g for g in gates if not g.passed]
        signal = float(len(failing))
        _t, _tok, usd = models.complete(
            cred, PATH,
            f"iteration {i}: {[g.name for g in failing]}",
            simulate=simulate,
        )
        if agent_fixes and failing:
            _apply_next_fix(ws.root, applied)
        return signal, usd

    res.loop = orch.run_loop(PATH, step)
    res.fixes_applied = applied

    res.gates = ev.run_gates(PATH, workdir=ws.root)
    artifact = _artifact(res)
    res.score = ev.judge(PATH, artifact)
    verdict = ev.decide(PATH, res.gates, res.score)
    res.action, res.reason = verdict.action, verdict.reason

    obs.end_span()
    obs.counter("path_runs", path=PATH)
    ws.cleanup()
    return res


def _apply_next_fix(root: Path, applied: list[str]) -> None:
    f = root / "sample_app" / "src" / "inventory.py"
    text = f.read_text()
    for name, old, new in FIXES:
        if name in applied:
            continue
        if old in text:
            text = text.replace(old, new)
            if name == "credential" and "import os" not in text:
                text = text.replace("import logging", "import logging\nimport os")
            f.write_text(text)
            applied.append(name)
            return


def _artifact(res: Result) -> str:
    """What the judge scores: the change summary the loop produced."""
    parts = ["Change summary for /validate-change."]
    if "stock-check" in res.fixes_applied:
        parts.append("reserve() now rejects an oversell, restoring the stock "
                     "invariant from ADR 0011.")
    if "credential" in res.fixes_applied:
        parts.append("The credential literal is gone; the token is read from "
                     "an environment variable at call time.")
    if "hot-path" in res.fixes_applied:
        parts.append("lookup() now indexes instead of scanning, per team "
                     "conventions on hot paths.")
    return " ".join(parts)
