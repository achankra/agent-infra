"""Checks Module 3 tasks."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.lab import Checker  # noqa: E402
from substrate import config  # noqa: E402
from substrate.identity import IdentityProvider  # noqa: E402
from substrate.observability import Observability  # noqa: E402
from substrate.policy import Decision, PolicyEngine, Tier  # noqa: E402


def main() -> int:
    c = Checker("Module 3: governance")
    obs = Observability()

    # Task 1: a workload identity for /validate-change
    ids = IdentityProvider(obs)
    has = "/validate-change" in ids.workloads
    c.task(1, "/validate-change has its own workload identity", has,
           "add a workload block for it in config/spiffe-ids.yaml")

    ttl_ok = False
    if has:
        ttl = int(ids.workloads["/validate-change"].get("ttl_seconds", 999999))
        ttl_ok = 0 < ttl <= 3600
    c.task(2, "its credential is short-lived (3600s or less)", ttl_ok,
           "set ttl_seconds to 3600 or less. One credential per task, "
           "short-lived, revocable.")

    # Task 3: ci:trigger must be reachable by that identity
    ent_ok = False
    if has:
        ent = ids.workloads["/validate-change"].get("entitlements", [])
        ent_ok = "ci:trigger" in ent and "scm:merge" not in ent
    c.task(3, "it can trigger CI but cannot merge", ent_ok,
           "entitlements should include ci:trigger and must not include "
           "scm:merge. ADR 0007 says agents do not merge.")

    # Task 4: deploy:production must be denied for that identity
    pol = PolicyEngine(obs)
    denied = False
    detail = ""
    if has:
        cred = ids.issue("/validate-change")
        v = pol.gate(cred, "deploy:production", payload="ship it")
        denied = v.decision is Decision.DENY
        detail = v.reason
    c.task(4, "a production deploy is stopped for that identity", denied,
           detail or "finish task 1 first")

    # Task 5: the injection in the real ticket is caught
    ticket = (config.ROOT / "sample_app/docs/tickets/PLAT-418.md").read_text()
    caught = pol.check_input(ticket).decision is Decision.DENY
    c.task(5, "the injection payload inside PLAT-418 is caught", caught,
           "the ticket contains an instruction pasted from a customer email. "
           "Add a pattern to injection_patterns in config/permission-tiers.yaml "
           "that catches it.")

    # Task 6: egress allowlist tightened
    doc = config.load_yaml("permission-tiers.yaml")
    allow = set(doc.get("egress_allowlist", []))
    external = [d for d in allow if not d.endswith(".acme.internal")]
    c.task(6, "the egress allowlist stays inside your perimeter", not external,
           f"these leave it: {', '.join(external)}. An agent that can post "
           f"output there can publish anything it was given.")

    # Task 7: audit retention is set as policy, not left to code
    otel = config.load_yaml("otel-collector.yaml")
    audit = otel.get("audit", {})
    retention_ok = bool(audit.get("immutable")) and int(audit.get("retention_days", 0)) >= 365
    c.task(7, "audit is immutable with at least a year of retention", retention_ok,
           "set immutable: true and retention_days >= 365 in "
           "config/otel-collector.yaml. Truncation is the common failure.")
    return c.report()


if __name__ == "__main__":
    raise SystemExit(main())
