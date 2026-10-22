"""Module 1: the substrate that runs paths.

Shows the ten pillars, which config artifact backs each one, and who holds
authority over the cost ceiling. Nothing is executed except the platform's
check of the loop's cost budget against the spend ceiling.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.lab import bullet, header, kv, section  # noqa: E402
from substrate import config  # noqa: E402
from substrate.observability import Observability  # noqa: E402
from substrate.orchestrator import Orchestrator  # noqa: E402

BLOCKS = {
    "governance": ("built once, enforced everywhere",
                   ["identity", "agent-security", "agent-observability"]),
    "harness": ("the machinery of one turn, configured per path",
                ["capability", "context", "execution", "evaluation"]),
    "models": ("what agents consume",
               ["providers", "inference-endpoints", "model-hosting"]),
}

ARTIFACTS = {
    "identity": "spiffe-ids.yaml",
    "agent-security": "permission-tiers.yaml",
    "agent-observability": "otel-collector.yaml",
    "capability": "tool-registry.yaml",
    "context": "rag-config.toml",
    "execution": "orchestrator.yaml",
    "evaluation": "gates.yaml",
    "providers": "providers.yaml",
    "inference-endpoints": "model-routes.toml",
    "model-hosting": "providers.yaml",
}

BUILT_IN = {"capability": 2, "identity": 3, "agent-security": 3,
            "agent-observability": 3, "context": 4, "execution": 5,
            "providers": 5, "inference-endpoints": 5, "model-hosting": 5,
            "evaluation": 6}


def main() -> int:
    header("Module 1: the substrate that runs paths",
           "Ten pillars. Every one is a file, not a concept.")

    for block, (tagline, pillars) in BLOCKS.items():
        section(f"{block}  ({tagline})")
        for p in pillars:
            art = ARTIFACTS[p]
            present = config.exists(art)
            mark = "present" if present else "not yet"
            kv(f"{p}", f"config/{art:<24} {mark}   built in module {BUILT_IN[p]}")

    section("Governance you inherit, the harness you declare")
    bullet("A new path inherits identity, policy and audit without asking.")
    bullet("It must declare its own context, tools, limits and definition of done.")
    bullet("")
    bullet("Test it in both directions:")
    bullet("  adding a path forces you to build a control  -> not built once")
    bullet("  adding a path requires no declaration        -> harness is not per-path")

    section("Blast radius decides who approves")
    print("""
      change a governance control          change a harness parameter
                |                                     |
        every path is affected                one path is affected
                |                                     |
        security owner reviews it            that path's team owns it

      One CI system, per-repo pipeline config. Nobody builds a CI system
      per service.
    """)

    section("What this repo already carries")
    kv("paths defined", "/pr-review, /validate-change")
    try:
        reg = config.load_yaml("tool-registry.yaml")
        kv("tools in registry", len(reg.get("tools", [])))
    except Exception as e:
        kv("tools in registry", f"unreadable: {e}")

    section("Who holds authority over the cost ceiling")
    obs = Observability()
    orch = Orchestrator(obs)
    asked = (config.load_yaml("orchestrator.yaml").get("bounds") or {}).get("cost_budget_usd")
    kv("platform ceiling", f"${orch.cost_ceiling_usd:.2f} per run  (config/budget-policy.yaml)")
    kv("path asks for", "not set" if asked is None else f"${float(asked):.2f}  (config/orchestrator.yaml)")
    if orch.cost_budget_clamped:
        kv("path is granted", f"${orch.cost_budget_usd:.2f}  CLAMPED to the ceiling")
        obs.flush()
        entry = next(a for a in obs.audit if a.get("decision") == "clamp")
        kv("ledger", f"{entry['action']} {entry['decision']} by {entry['identity']}, "
                     f"asked {entry['asked']}, granted {entry['granted']}")
        bullet("")
        bullet(entry["reason"])
        print("\n  Now set cost_budget_usd back to null in config/orchestrator.yaml.")
        print("  Module 5 starts with every bound unset.\n")
    elif asked is not None:
        kv("path is granted", f"${float(asked):.2f}  within the ceiling")
        print()
    else:
        print("\n  Try it: set bounds.cost_budget_usd in config/orchestrator.yaml to 9.00,")
        print("  run this again, then set it back to null.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
