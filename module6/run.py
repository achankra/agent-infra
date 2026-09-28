"""Module 6: whether the output ships.

Gates decide. The judge scores and routes. Runs both against a real artifact.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.lab import bullet, dashboard_note, header, kv, section  # noqa: E402
from substrate import config  # noqa: E402
from substrate.evaluation import Evaluator  # noqa: E402
from substrate.observability import Observability  # noqa: E402
from substrate.paths import validate_change  # noqa: E402

GOOD = ("Change summary. reserve() now rejects an oversell, restoring the "
        "stock invariant from ADR 0011. The credential literal is gone; the "
        "token is read from an environment variable at call time.")
WEAK = ("Fixed some things in the inventory module. Unclear whether the "
        "sk-inventory token still needs rotating.")


def main() -> int:
    header("Module 6: evaluation",
           "Deterministic gates decide. The judge scores and routes.")

    obs = Observability()
    ev = Evaluator(obs)

    section("The definition of done, as gates with exit codes")
    for g in ev.gates_doc.get("gates", []):
        kv(g["name"], f"{g.get('category','functional'):<12} {g['run']}")
    bullet("")
    bullet("No model is consulted anywhere in gates.yaml.")

    print("""
      artifact --> [ gates: exit codes ] --fail--> back to the loop
                          |
                         pass
                          v
                   [ judge: score ] --low--> a person decides
                                    --high-> promote

      The judge never hard-fails the loop. Across 21 judges and roughly
      541,000 judgments, rankings moved by up to 14 positions across
      benchmarks, and production judges stayed consistent with themselves
      while staying biased. A rubric narrows the gap; it does not close it.
    """)

    section("The rubric")
    rubric = ev.rubrics.get("/validate-change")
    if not rubric:
        bullet("no rubric for /validate-change yet")
    else:
        for crit in rubric.get("criteria", []):
            kv(crit["name"], f"weight {crit.get('weight',1)}  "
                             f"look_for {crit.get('look_for')}")
        for band in rubric.get("bands", []):
            kv(f"band {band['name']}", f">= {band['min_score']} -> {band.get('route')}")

    section("Two artifacts, same rubric")
    for label, art in (("well-formed summary", GOOD), ("weak summary", WEAK)):
        s = ev.judge("/validate-change", art)
        if s:
            kv(label, f"score {s.total}  band {s.band}  routes to {s.route}")
            for k, v in s.per_criterion.items():
                print(f"        {k:<28} {v}")

    section("Run the path, gates and judge together")
    res = validate_change.run(obs)
    kv("gates", ", ".join(f"{g.name}={'pass' if g.passed else 'fail'}"
                          for g in res.gates))
    if res.score:
        kv("score", f"{res.score.total} ({res.score.band})")
    kv("action", f"{res.action}  {res.reason}")

    obs.flush()
    dashboard_note()
    section("Operating metrics, once the gates pass")
    bullet("Gates say whether this artifact ships. These say whether the path works.")
    slos = config.load_yaml("agent-slos.yaml").get("metrics", {})
    for name, m in slos.items():
        kv(name, f"healthy {m['healthy']}   |   look at it {m['investigate_at']}")
    bullet("Nothing gates on these. They are what you watch in week two.")
    bullet("The Platform Engineer's Handbook, Ch 14, Table 14.3.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
