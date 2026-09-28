"""Checks Module 5 tasks."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.lab import Checker  # noqa: E402
from substrate import config  # noqa: E402
from substrate.models import ModelError, ModelGateway  # noqa: E402
from substrate.observability import Observability  # noqa: E402
from substrate.orchestrator import Orchestrator, Stop  # noqa: E402
from substrate.paths import validate_change  # noqa: E402


def main() -> int:
    c = Checker("Module 5: execution and models")
    obs = Observability()
    orch = Orchestrator(obs)

    c.task(1, "an iteration cap is set", bool(orch.iteration_cap),
           "set bounds.iteration_cap in config/orchestrator.yaml")
    c.task(2, "stall detection is set", bool(orch.stall_window),
           "set bounds.stall_window. Stalling usually means an ambiguous goal "
           "or missing context, so detect it rather than raising the ceiling.")
    c.task(3, "a cost budget is set", bool(orch.cost_budget_usd),
           "set bounds.cost_budget_usd. Unconstrained agents were measured at "
           "the lab measures it: $0.0150 unbounded against $0.0004 bounded.")

    # Task 4: with the stops in place, a non-converging loop must stop by design
    stopped_by_design = False
    detail = ""
    if all((orch.iteration_cap, orch.stall_window, orch.cost_budget_usd)):
        res = validate_change.run(Observability(), agent_fixes=False)
        stopped_by_design = res.loop.stop is not Stop.UNBOUNDED
        detail = f"stopped on {res.loop.stop.value} after {res.loop.iterations}"
    c.task(4, "a loop that cannot converge still stops", stopped_by_design,
           detail or "finish tasks 1 to 3 first")

    # Task 5: swap the model behind the route
    routes = config.load_toml("model-routes.toml")
    pr = routes.get("by_path", {}).get("/pr-review", {}).get("model")
    c.task(5, "/pr-review is routed to the cheaper model", pr == "small",
           f"currently routed to {pr}. Read-only review does not need the "
           f"expensive model. Change it in config/model-routes.toml; it is "
           f"one line, and no code moves.")

    # Task 6: confidential work must not route to a managed model
    models = ModelGateway(obs)
    ok = False
    why = ""
    try:
        spec = models.resolve("/validate-change", data_class="confidential")
        ok = spec.hosting in ("self-hosted", "private-tenancy")
        why = f"{spec.model_id} is {spec.hosting}"
    except ModelError as e:
        why = str(e)
    c.task(6, "confidential data has a route that accepts it", ok,
           f"{why}. Add a by_path route, or raise max_data_class on a model "
           f"that is actually hosted where confidential data may go.")

    # Task 7: no unapproved provider is reachable
    reachable = set()
    for p in routes.get("by_path", {}).values():
        mid = p.get("model")
        if mid in models.models:
            reachable.add(models.models[mid].provider)
    if models.default in models.models:
        reachable.add(models.models[models.default].provider)
    unapproved = [p for p in reachable
                  if models.providers.get(p) and models.providers[p].status != "approved"]
    c.task(7, "every reachable provider is approved", not unapproved,
           f"unapproved and reachable: {unapproved}")
    return c.report()


if __name__ == "__main__":
    raise SystemExit(main())
