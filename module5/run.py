"""Module 5: where agents run, and what stops them.

Run it once with the shipped config and the loop is unbounded. Add the three
stops and run it again.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.lab import bullet, dashboard_note, header, kv, section  # noqa: E402
from substrate.models import ModelGateway, ModelError  # noqa: E402
from substrate.observability import Observability  # noqa: E402
from substrate.orchestrator import Orchestrator  # noqa: E402
from substrate.paths import validate_change  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-fix", action="store_true",
                    help="the agent proposes nothing, so the loop cannot converge")
    ap.add_argument("--live", action="store_true", help="call a real model")
    args = ap.parse_args()

    header("Module 5: execution and models",
           "One workspace per run. Three ways to stop. One model gateway.")

    obs = Observability()
    orch = Orchestrator(obs)

    section("The sandbox")
    kv("kind", orch.sandbox_kind)
    kv("network", orch.network)
    kv("control mode /validate-change", orch.mode_for("/validate-change").value)

    section("The three stops")
    for name, val in (("iteration_cap", orch.iteration_cap),
                      ("stall_window", orch.stall_window),
                      ("cost_budget_usd", orch.cost_budget_usd)):
        kv(name, val if val is not None else "not set")
    if not any((orch.iteration_cap, orch.stall_window, orch.cost_budget_usd)):
        bullet("")
        bullet("No stop is configured. The loop will run until a hard limit")
        bullet("in the runner catches it, which is not a design.")

    section("The model gateway")
    models = ModelGateway(obs)
    kv("default route", models.default)
    kv("fallback on error", models.fallback)
    kv("quota per run", f"{models.quota_tokens} tokens")
    for path_name, spec in models.by_path.items():
        try:
            m = models.resolve(path_name)
            kv(path_name, f"{m.model_id} pinned to {m.pinned_version} "
                          f"({m.hosting}, up to {m.data_class})")
        except ModelError as e:
            kv(path_name, f"ERROR {e}")

    print("""
      agent --\\                          the tool gateway governs what an
      agent ---> [ model gateway ] -->    agent can DO. this one governs
      agent --/    routing                what it can THINK WITH.
                   brokered keys
                   quotas                 clients authenticate here, never
                   metering               to the provider.
    """)

    section("Confidential data has to route somewhere it is allowed")
    for dc in ("internal", "confidential"):
        try:
            m = models.resolve("/validate-change", data_class=dc)
            kv(dc, f"routes to {m.model_id} ({m.hosting})")
        except ModelError as e:
            kv(dc, f"BLOCKED  {e}")

    section("Run /validate-change")
    res = validate_change.run(obs, simulate=not args.live,
                              agent_fixes=not args.no_fix)
    kv("stop reason", res.loop.stop.value)
    kv("iterations", res.loop.iterations)
    kv("spent", f"${res.loop.usd:.4f}")
    kv("checkpoints", res.loop.checkpoints)
    kv("fixes applied", res.fixes_applied or "none")
    kv("gates", ", ".join(f"{g.name}={'pass' if g.passed else 'fail'}"
                          for g in res.gates))
    kv("workspace", f"{res.workspace} (removed on exit)")

    if res.loop.stop.value == "still-running":
        bullet("")
        bullet("The loop hit the runner's hard limit, not one of your stops.")
        bullet("Open config/orchestrator.yaml and set the three bounds.")

    obs.flush()
    print("\n" + obs.summary())
    dashboard_note()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
