"""Checks Module 8 tasks."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import yaml  # noqa: E402
from scripts.lab import Checker  # noqa: E402
from substrate import config  # noqa: E402

MANIFEST = "workload-manifests/finance-reconciliation.yaml"
MODES = {"assistive", "task", "workflow", "bounded-autonomy"}
CLASSES = {"public", "internal", "confidential"}


def main() -> int:
    c = Checker("Module 8: enterprise agentic workloads")
    doc = yaml.safe_load((config.CONFIG / MANIFEST).read_text()) or {}

    def val(*keys):
        cur = doc
        for k in keys:
            cur = (cur or {}).get(k) if isinstance(cur, dict) else None
        return cur

    c.task(1, "the workload has a named domain owner",
           _filled(doc.get("owner")),
           f"set owner in config/{MANIFEST}")

    ttl = val("identity", "ttl_seconds")
    c.task(2, "its credential is short-lived",
           isinstance(ttl, int) and 0 < ttl <= 3600,
           "identity.ttl_seconds must be an integer, 3600 or less. The rule "
           "does not change because the workload is finance.")

    ents = val("identity", "entitlements") or []
    real = [e for e in ents if _filled(e)]
    c.task(3, "entitlements are operations, not systems",
           len(real) >= 2 and all(":" in str(e) for e in real),
           f"got {real}. Use the same shape as the software paths, for "
           f"example ledger:read, ledger:post.")

    dc = val("context", "data_class")
    c.task(4, "the data class is declared", dc in CLASSES,
           f"context.data_class must be one of {sorted(CLASSES)}. Finance "
           f"reconciliation is not internal by default.")

    mode = val("execution", "control_mode")
    c.task(5, "a control mode is granted", mode in MODES,
           f"execution.control_mode must be one of {sorted(MODES)}")

    cap = val("execution", "iteration_cap")
    budget = val("execution", "cost_budget_usd")
    c.task(6, "the loop has bounds",
           isinstance(cap, int) and cap > 0
           and isinstance(budget, (int, float)) and budget > 0,
           "iteration_cap and cost_budget_usd. Every loop needs a way to stop, "
           "whatever the domain.")

    dod = val("evaluation", "definition_of_done")
    routes = str(val("evaluation", "low_score_routes_to") or "").lower()
    c.task(7, "done is defined and a low score routes to a person",
           _filled(dod) and routes in ("human", "review", "single-review"),
           "definition_of_done must say what a deterministic gate checks, and "
           "low_score_routes_to must never be 'fail'.")

    target = val("cost", "target_usd")
    c.task(8, "cost per workflow has a target",
           isinstance(target, (int, float)) and target > 0,
           "cost.target_usd. This is the number leadership asks for.")

    # 9: the substrate itself was not modified
    tiers = config.load_yaml("permission-tiers.yaml")
    unchanged = set((tiers.get("tiers") or {}).keys()) == {"safe", "moderate", "dangerous"}
    c.task(9, "the workload needed no new governance block", unchanged,
           "a finance workload should not have forced a fourth tier. If it "
           "did, the tier map was software-specific.")
    return c.report()


def _filled(v) -> bool:
    return v is not None and str(v).strip().upper() != "TODO" and str(v).strip() != ""


if __name__ == "__main__":
    raise SystemExit(main())
