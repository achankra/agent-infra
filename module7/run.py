"""Module 7: the full path build.

Runs /pr-review through every pillar in firing order, then breaks one pillar at
a time so you see what each failure looks like.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.lab import bullet, dashboard_note, header, kv, section  # noqa: E402
from substrate.observability import Observability  # noqa: E402
from substrate.paths import pr_review, validate_change  # noqa: E402

BREAKS = {
    "identity": "remove the workload block for the path from config/spiffe-ids.yaml",
    "capability": "remove the operation from config/entitlement-map.yaml",
    "gateway": "remove the server from enabled_servers in config/mcp-gateway.tf",
    "context": "remove the data contract from config/data-contracts/",
    "models": "point the route at an unapproved provider in config/model-routes.toml",
    "execution": "set every bound to null in config/orchestrator.yaml",
    "evaluation": "delete the rubric from config/eval-rubrics/",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()

    header("Module 7: the full path build",
           "Every pillar in order, on one path.")

    section("Firing order, derived from necessity")
    print("""
      identity ---> context ---> capability ---> model ---> evaluation
         |             |             |             |            |
      binds first   assembled    checked        routed      judges an
      because       for a        before a       then        artifact that
      context is    principal    tool fires     called      now exists
      assembled
      for a
      principal

      security wraps every turn.   observability spans the whole run.
    """)

    obs = Observability()

    section("/pr-review, read-only, the lowest-risk way in")
    r = pr_review.run(obs, simulate=not args.live, attempt_merge=True)
    kv("identity", r.identity)
    kv("context", f"{r.context_sources} ({r.context_tokens} tokens)")
    if r.dropped_sources:
        for name, why in r.dropped_sources:
            kv(f"  dropped {name}", why)
    kv("capability", ", ".join(r.tools_available))
    kv("model", r.model)
    for op, ok, why in r.tool_calls:
        kv(f"  {op}", "allowed" if ok else f"STOPPED  {why}")
    kv("cost", f"${r.usd:.4f}")

    section("/validate-change, the hybrid loop")
    v = validate_change.run(obs, simulate=not args.live)
    kv("control mode", v.mode)
    kv("stop", f"{v.loop.stop.value} after {v.loop.iterations} iterations")
    kv("fixes", v.fixes_applied or "none")
    kv("gates", ", ".join(f"{g.name}={'pass' if g.passed else 'fail'}"
                          for g in v.gates))
    if v.score:
        kv("score", f"{v.score.total} ({v.score.band}) -> {v.score.route}")
    kv("action", f"{v.action}  {v.reason}")

    section("What breaks when a pillar is missing")
    for pillar, how in BREAKS.items():
        kv(pillar, how)
    bullet("")
    bullet("Identity is the one worth naming: its failure produces no")
    bullet("postmortem, because the failure is the inability to attribute.")

    obs.flush()
    print("\n" + obs.summary())
    dashboard_note()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
