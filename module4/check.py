"""Checks Module 4 tasks."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.lab import Checker  # noqa: E402
from substrate import config  # noqa: E402
from substrate.context import ContextAssembler  # noqa: E402
from substrate.observability import Observability  # noqa: E402


def main() -> int:
    c = Checker("Module 4: what the agent knows")
    obs = Observability()
    ctx = ContextAssembler(obs)
    wanted = ctx.cfg.get("paths", {}).get("/pr-review", {}).get("sources", [])

    c.task(1, "/pr-review is given the ADRs", "adrs" in wanted,
           "add \"adrs\" to sources under [paths.\"/pr-review\"] in "
           "config/rag-config.toml. It is knowledge, retrieved by RAG.")

    c.task(2, "/pr-review is given the ticket", "ticket" in wanted,
           "add \"ticket\". It is a live system, retrieved by MCP.")

    contracts = ctx.contracts
    tc = contracts.get("ticket")
    c.task(3, "the ticket has a data contract", tc is not None,
           "create config/data-contracts/ticket.yaml with source, owner, "
           "certified, schema, semantics, quality_rules and sla. A source "
           "without a contract is not assembled, it is reported.")

    c.task(4, "the ticket contract is certified", bool(tc and tc.get("certified")),
           "set certified: true once you have named an owner and an SLA")

    a = ctx.assemble("/pr-review")
    got = set(a.names)
    c.task(5, "all three sources actually assemble", {"diff", "adrs", "ticket"} <= got,
           f"assembled: {sorted(got) or 'none'}. Dropped: "
           f"{[n for n, _ in a.dropped] or 'none'}")

    trigger = int(ctx.window * ctx.compact_at)
    c.task(6, "the assembly stays under the compaction trigger or compacts",
           a.tokens <= trigger,
           f"{a.tokens} tokens against a {trigger}-token trigger "
           f"({ctx.window} window x {ctx.compact_at}). Raise max_tokens, lower "
           f"compact_at_fraction, or drop a source. Decide which, and know why.")

    everything = ctx._read({"path": "sample_app"})
    from substrate.context import _tok
    c.task(7, "the governed assembly is smaller than dumping everything",
           0 < a.tokens < _tok(everything),
           f"governed {a.tokens} tokens against {_tok(everything)} for the "
           f"whole tree")
    return c.report()


if __name__ == "__main__":
    raise SystemExit(main())
