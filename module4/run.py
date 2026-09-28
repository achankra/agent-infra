"""Module 4: what the agent knows.

Assembles context for /pr-review under the current config, then shows the same
path against a dump-everything baseline so the difference is a number.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.lab import bullet, dashboard_note, header, kv, section  # noqa: E402
from substrate.context import ContextAssembler  # noqa: E402
from substrate.observability import Observability  # noqa: E402
from substrate.policy import PolicyEngine  # noqa: E402


def main() -> int:
    header("Module 4: what the agent knows",
           "And what it assumes because you did not tell it.")

    obs = Observability()
    ctx = ContextAssembler(obs)

    section("The window exists per turn. It is not memory.")
    kv("max_tokens", ctx.window)
    kv("compaction trigger", f"{int(ctx.window * ctx.compact_at)} tokens "
                             f"({int(ctx.compact_at * 100)}% of the window)")
    print("""
      accuracy
        ^
        |  ####                      ####      a fact at the start or the end
        |      ##                  ##          is recalled; the same fact in
        |        ####          ####            the middle is not
        |            ##########
        +-------------------------------> position in the window

      Compaction runs before the window degrades. A summary written after rot
      has set in is itself degraded, because the model producing it is already
      impaired. The trigger point is the design decision.
    """)

    section("Assembled for /pr-review")
    a = ctx.assemble("/pr-review")
    for s in a.sources:
        kv(s.name, f"{s.kind:<10} via {s.retrieval:<5} {s.tokens:>5} tokens  "
                   f"owner {s.owner}")
    kv("total", f"{a.tokens} tokens")
    if a.dropped:
        section("Dropped, and why")
        for name, why in a.dropped:
            kv(name, why)
    if a.compacted:
        bullet("compaction ran before the window filled")

    section("The dump-everything baseline")
    everything = ctx._read({"path": "sample_app"})
    from substrate.context import _tok
    kv("every file under sample_app", f"{_tok(everything)} tokens")
    kv("governed assembly", f"{a.tokens} tokens")
    if a.tokens:
        kv("ratio", f"{_tok(everything) / a.tokens:.1f}x more, "
                    f"none of it certified")

    section("Retrieval is RAG for knowledge, MCP for live systems")
    for name, spec in (ctx.cfg.get("sources") or {}).items():
        kv(name, f"{spec.get('kind','?'):<10} {spec.get('retrieval','?')}")

    section("A live source is untrusted input")
    pol = PolicyEngine(obs)
    ticket = Path("sample_app/docs/tickets/PLAT-418.md")
    if ticket.exists():
        v = pol.check_input(ticket.read_text())
        kv("PLAT-418 screened", f"{v.decision.value}  {v.reason}")
        if v.decision.value != "deny":
            bullet("This ticket carries an instruction and is being allowed.")
            bullet("Module 3 Task 5 adds the pattern that catches it.")
        bullet("A ticket is data. If it is assembled into context without")
        bullet("screening, its contents become instructions.")

    obs.flush()
    dashboard_note()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
