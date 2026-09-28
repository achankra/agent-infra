"""Module 8: the same pillars, beyond software delivery.

Loads every declared workload, software and otherwise, and shows that they
differ only in parameters.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import yaml  # noqa: E402
from scripts.lab import bullet, header, kv, section  # noqa: E402
from substrate import config  # noqa: E402
from substrate.identity import IdentityProvider  # noqa: E402
from substrate.observability import Observability  # noqa: E402
from substrate.orchestrator import Orchestrator  # noqa: E402

PILLARS = ["identity", "agent-security", "agent-observability", "capability",
           "context", "execution", "evaluation", "providers",
           "inference-endpoints", "model-hosting"]


def main() -> int:
    header("Module 8: enterprise agentic workloads",
           "Platform engineers own the substrate. Domain teams own the workflow.")

    obs = Observability()

    section("Software paths on this substrate")
    ids = IdentityProvider(obs)
    orch = Orchestrator(obs)
    for p in sorted(ids.workloads):
        kv(p, f"control mode {orch.mode_for(p).value}")

    section("Non-software workloads declared against the same pillars")
    d = config.CONFIG / "workload-manifests"
    manifests = sorted(d.glob("*.yaml")) if d.exists() else []
    if not manifests:
        bullet("none yet")
    for f in manifests:
        doc = yaml.safe_load(f.read_text()) or {}
        todo = _todo_count(doc)
        kv(doc.get("path", f.stem),
           f"{doc.get('domain','?'):<12} owner {doc.get('owner','?'):<18} "
           f"{todo} fields still TODO")

    section("The pillars do not change")
    print("""
      /pr-review          /reconcile-ledger      /campaign-brief
      software            finance                marketing
           \\                   |                      /
            \\                  |                     /
             +----------- same ten pillars ---------+
                   identity   security   observability
                   capability context    execution    evaluation
                   providers  endpoints  hosting

      What changes between them is every parameter, and nothing else.
    """)

    section("The proof point")
    kv("Sonnet 4.5 under SWE-Agent", "68%")
    kv("Sonnet 4.5 under HAL Generalist", "34%")
    kv("same weights, same tasks", "34 points, arXiv:2605.23950")
    bullet("Throughput and reliability come from the platform, not the model.")

    section("What leadership asks for")
    kv("cost per workflow", "what leadership asks for. You derive it")
    kv("a maturity roadmap", "staged, not a big-bang rollout")
    return 0


def _todo_count(doc, n=0) -> int:
    if isinstance(doc, dict):
        return sum(_todo_count(v) for v in doc.values())
    if isinstance(doc, list):
        return sum(_todo_count(v) for v in doc)
    return 1 if str(doc).strip().upper() == "TODO" else 0


if __name__ == "__main__":
    raise SystemExit(main())
