"""Checks Module 7, the capstone.

Every pillar must be configured and the whole path must run clean.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.lab import Checker  # noqa: E402
from substrate import config  # noqa: E402
from substrate.context import ContextAssembler  # noqa: E402
from substrate.evaluation import Evaluator  # noqa: E402
from substrate.identity import IdentityProvider  # noqa: E402
from substrate.models import ModelGateway  # noqa: E402
from substrate.observability import Observability  # noqa: E402
from substrate.orchestrator import Orchestrator, Stop  # noqa: E402
from substrate.paths import pr_review, validate_change  # noqa: E402
from substrate.registry import ToolRegistry  # noqa: E402

NEW_PATH = "/oncall-triage"


def main() -> int:
    c = Checker("Module 7: the full path build")
    obs = Observability()

    # 1-3: the substrate is complete
    ids = IdentityProvider(obs)
    c.task(1, "both shipped paths have identities",
           {"/pr-review", "/validate-change"} <= set(ids.workloads),
           "Module 3 adds /validate-change to config/spiffe-ids.yaml")

    orch = Orchestrator(obs)
    c.task(2, "all three stops are configured",
           all((orch.iteration_cap, orch.stall_window, orch.cost_budget_usd)),
           "Module 5 sets bounds in config/orchestrator.yaml")

    ev = Evaluator(obs)
    c.task(3, "both paths have a rubric",
           {"/pr-review", "/validate-change"} <= set(ev.rubrics),
           "Module 6 adds config/eval-rubrics/pr-review.yaml")

    # 4-5: the paths run clean
    r = pr_review.run(Observability(), attempt_merge=True)
    merge_stopped = any(op == "scm:merge" and not ok for op, ok, _ in r.tool_calls)
    others_ok = all(ok for op, ok, _ in r.tool_calls if op != "scm:merge")
    c.task(4, "/pr-review completes and the merge is still stopped",
           merge_stopped and others_ok,
           f"calls: {[(o, k) for o, k, _ in r.tool_calls]}")

    v = validate_change.run(Observability())
    c.task(5, "/validate-change converges and promotes",
           v.loop.stop is Stop.CONVERGED and v.action == "promote",
           f"stopped {v.loop.stop.value}, action {v.action}: {v.reason}")

    # 6-8: a third path, declared not built
    reg = ToolRegistry()
    ctx = ContextAssembler(obs)
    models = ModelGateway(obs)
    declared = [
        (NEW_PATH in ids.workloads, "config/spiffe-ids.yaml"),
        (NEW_PATH in reg.entitlements, "config/entitlement-map.yaml"),
        (NEW_PATH in ctx.cfg.get("paths", {}), "config/rag-config.toml"),
        (NEW_PATH in models.by_path, "config/model-routes.toml"),
        (NEW_PATH in orch.control_modes, "config/orchestrator.yaml"),
        (NEW_PATH in ev.rubrics, "config/eval-rubrics/"),
    ]
    missing = [where for ok, where in declared if not ok]
    c.task(6, f"{NEW_PATH} is declared across the harness", not missing,
           f"still missing from: {', '.join(missing)}")

    c.task(7, f"{NEW_PATH} needed no new governance control",
           _no_new_governance(),
           "you should not have edited permission-tiers.yaml structure or "
           "added a second policy engine. Governance is built once.")

    ran = False
    detail = ""
    if not missing:
        try:
            cred = ids.issue(NEW_PATH)
            ran = bool(cred.entitlements)
            detail = f"issued {cred} with {len(cred.entitlements)} entitlements"
        except Exception as e:
            detail = str(e)
    c.task(8, f"{NEW_PATH} can be issued an identity and run", ran,
           detail or "finish task 6 first")
    return c.report()


def _no_new_governance() -> bool:
    """The tier map may gain operations. It must still have exactly three tiers
    and the same three rules, because widening those is a platform decision."""
    doc = config.load_yaml("permission-tiers.yaml")
    tiers = set((doc.get("tiers") or {}).keys())
    rules = set((doc.get("rules") or {}).keys())
    return tiers == {"safe", "moderate", "dangerous"} and rules == tiers


if __name__ == "__main__":
    raise SystemExit(main())
