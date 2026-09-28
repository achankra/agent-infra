"""Checks Module 6 tasks."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.lab import Checker  # noqa: E402
from substrate import config  # noqa: E402
from substrate.evaluation import Evaluator  # noqa: E402
from substrate.observability import Observability  # noqa: E402

WEAK = ("Fixed some things in the inventory module. Unclear whether the "
        "sk-inventory token still needs rotating.")
STRONG = ("reserve() rejects an oversell per ADR 0011 stock invariant. "
          "The token is read from an environment variable at call time.")


def main() -> int:
    c = Checker("Module 6: evaluation")
    obs = Observability()
    ev = Evaluator(obs)

    r = ev.rubrics.get("/pr-review")
    c.task(1, "/pr-review has a rubric", r is not None,
           "create config/eval-rubrics/pr-review.yaml with path: /pr-review")

    crits = (r or {}).get("criteria", [])
    c.task(2, "it has at least three weighted criteria", len(crits) >= 3,
           f"{len(crits)} defined. A rubric with one criterion is a preference.")

    bands = (r or {}).get("bands", [])
    routes = {b.get("route") for b in bands}
    c.task(3, "it has three bands that route differently", len(bands) >= 3
           and len(routes) >= 3,
           f"bands: {[b.get('name') for b in bands]}, routes: {sorted(routes)}. "
           f"A low score routes to a human; it does not fail the loop.")

    weak = ev.judge("/pr-review", WEAK)
    strong = ev.judge("/pr-review", STRONG)
    c.task(4, "the rubric separates a weak artifact from a strong one",
           bool(weak and strong and strong.total > weak.total),
           f"weak {getattr(weak,'total',None)} against strong "
           f"{getattr(strong,'total',None)}. Use penalize as well as look_for.")

    c.task(5, "a low score routes to a person, never to a failure",
           bool(weak and weak.route in ("human", "single-review")),
           f"weak artifact routed to {getattr(weak,'route',None)}")

    # Task 6: add an architectural gate
    gates = config.load_yaml("gates.yaml").get("gates", [])
    names = {g["name"] for g in gates}
    arch = [g for g in gates if g.get("category") == "architectural"]
    c.task(6, "an architectural gate exists", bool(arch),
           "add a gate with category: architectural to config/gates.yaml. "
           "One is provided: scripts/check_hot_path.py")

    runs = True
    detail = ""
    for g in gates:
        proc = subprocess.run(g["run"], shell=True, cwd=str(config.ROOT),
                              capture_output=True, text=True)
        if proc.returncode not in (0, 1):
            runs = False
            detail = f"{g['name']} exited {proc.returncode}: {proc.stderr.strip()[:80]}"
    c.task(7, "every gate command actually runs", runs,
           detail or "a gate that cannot run is not a gate")
    c.task(8, "the seeded defects are still catchable",
           "functional" in names and "policy-secrets" in names,
           "do not delete the shipped gates")
    return c.report()


if __name__ == "__main__":
    raise SystemExit(main())
