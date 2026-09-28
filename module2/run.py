"""Module 2: the tooling layer and the capability pillar.

Shows the registry, the entitlement map and the gateway as three separate
decisions, then runs /pr-review through them.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.lab import bullet, dashboard_note, header, kv, section  # noqa: E402
from substrate import config  # noqa: E402
from substrate.observability import Observability  # noqa: E402
from substrate.paths import pr_review  # noqa: E402
from substrate.registry import ToolRegistry  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default="/pr-review")
    args = ap.parse_args()

    header("Module 2: what agents reach into",
           "The tool is the system. The capability is the grant.")

    reg = ToolRegistry()

    section("Layer 1 systems, and the operations each one yields")
    for system, ops in reg.systems().items():
        kv(system, ", ".join(ops))
    print("\n      One system, many grants. The unit of governance is the")
    print("      operation, not the system.")

    section("The gateway: two doors, both must be open")
    tf = config.read_tf_locals("mcp-gateway.tf")
    kv("enabled_servers", ", ".join(tf.get("enabled_servers", [])))
    kv("rate_limit_per_minute", tf.get("rate_limit_per_minute"))
    known = set(reg.systems())
    off = sorted(known - set(tf.get("enabled_servers", [])))
    if off:
        kv("registered but unreachable", ", ".join(off))

    print("""
      agent --\\
      agent ---> [ tool gateway ] --> github
      agent --/    authz              argocd
                   rate limit         prometheus
                   audit
    """)

    section(f"What {args.path} is entitled to")
    tools = reg.for_path(args.path)
    for t in tools:
        kv(t.operation, f"{t.system:<16} {t.token_cost} tokens  {t.description}")
    kv("", "")
    kv("tool definitions cost", f"{reg.context_cost(args.path)} tokens before any work")
    warn = reg.curation_warning(args.path)
    if warn:
        bullet(f"WARNING {warn}")

    section("Run the path")
    obs = Observability()
    res = pr_review.run(obs)
    for op, ok, why in res.tool_calls:
        kv(op, ("allowed" if ok else f"DENIED  {why}"))
    kv("model", res.model)
    kv("context", f"{res.context_sources} ({res.context_tokens} tokens)")
    obs.flush()
    print("\n" + obs.summary())
    dashboard_note()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
