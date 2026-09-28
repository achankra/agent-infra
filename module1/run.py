"""Module 1: the substrate that runs paths.

Shows the ten pillars, which config artifact backs each one, and which of them
this repo can already load. Nothing is executed. This module is the map.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.lab import bullet, header, kv, section  # noqa: E402
from substrate import config  # noqa: E402

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

    print("\n  Now open module1/pillars.yaml and fill in the TODO fields.")
    print("  Then run: python3 module1/check.py\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
