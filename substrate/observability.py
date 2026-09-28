"""Traces, metrics and the audit ledger. Governance, built once.

Every platform decision is recorded against an identity. A run that cannot be
attributed is the one failure mode that produces no postmortem, because the
failure is the inability to attribute.
"""
from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

STATE = Path(__file__).resolve().parent.parent / ".state"


@dataclass
class Span:
    name: str
    identity: str
    started: float = field(default_factory=time.time)
    ended: float | None = None
    attributes: dict = field(default_factory=dict)
    children: list["Span"] = field(default_factory=list)

    def end(self) -> "Span":
        self.ended = time.time()
        return self

    @property
    def ms(self) -> float:
        return round(((self.ended or time.time()) - self.started) * 1000, 2)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "identity": self.identity,
            "duration_ms": self.ms,
            "attributes": self.attributes,
            "children": [c.to_dict() for c in self.children],
        }


class Observability:
    """One collector per run. Emits Prometheus text and a JSON audit ledger."""

    def __init__(self, run_id: str | None = None) -> None:
        self.run_id = run_id or uuid.uuid4().hex[:8]
        self.spans: list[Span] = []
        self._stack: list[Span] = []
        self.counters: dict[tuple[str, tuple], int] = {}
        self.gauges: dict[tuple[str, tuple], float] = {}
        self.audit: list[dict] = []
        self.cost: dict[str, float] = {}

    # -- traces -------------------------------------------------------
    def span(self, name: str, identity: str, **attrs) -> Span:
        s = Span(name=name, identity=identity, attributes=attrs)
        if self._stack:
            self._stack[-1].children.append(s)
        else:
            self.spans.append(s)
        self._stack.append(s)
        return s

    def end_span(self) -> None:
        if self._stack:
            self._stack.pop().end()

    # -- metrics ------------------------------------------------------
    def counter(self, name: str, value: int = 1, **labels) -> None:
        key = (name, tuple(sorted(labels.items())))
        self.counters[key] = self.counters.get(key, 0) + value

    def gauge(self, name: str, value: float, **labels) -> None:
        self.gauges[(name, tuple(sorted(labels.items())))] = value

    def spend(self, path: str, usd: float) -> None:
        self.cost[path] = round(self.cost.get(path, 0.0) + usd, 6)
        self.gauge("agent_cost_usd", self.cost[path], path=path)

    # -- audit --------------------------------------------------------
    def record(self, identity: str, action: str, decision: str, **detail) -> None:
        """Every action and every platform decision, attributable to an identity."""
        self.audit.append(
            {
                "run_id": self.run_id,
                "ts": round(time.time(), 3),
                "identity": identity,
                "action": action,
                "decision": decision,
                **detail,
            }
        )
        self.counter("governance_events", action=action, decision=decision)

    # -- export -------------------------------------------------------
    def prometheus(self) -> str:
        lines = []
        for (name, labels), v in sorted(self.counters.items(), key=lambda x: str(x[0])):
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{name}{_lbl(labels)} {v}")
        for (name, labels), v in sorted(self.gauges.items(), key=lambda x: str(x[0])):
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name}{_lbl(labels)} {v}")
        return "\n".join(lines) + "\n"

    def flush(self) -> Path:
        STATE.mkdir(exist_ok=True)
        (STATE / "metrics.prom").write_text(self.prometheus())
        (STATE / "audit.json").write_text(json.dumps(self.audit, indent=2))
        (STATE / "traces.json").write_text(
            json.dumps([s.to_dict() for s in self.spans], indent=2)
        )
        return STATE

    def summary(self) -> str:
        out = [f"  run {self.run_id}"]
        out.append(f"  spans      {len(self.spans)} root, {_count(self.spans)} total")
        out.append(f"  audit      {len(self.audit)} entries")
        ids = sorted({a['identity'] for a in self.audit})
        out.append(f"  identities {', '.join(ids) if ids else 'none'}")
        if self.cost:
            for p, c in self.cost.items():
                out.append(f"  cost       {p}: ${c:.4f}")
        return "\n".join(out)


def _lbl(labels: tuple) -> str:
    if not labels:
        return ""
    inner = ",".join(f'{k}="{v}"' for k, v in labels)
    return "{" + inner + "}"


def _count(spans: list[Span]) -> int:
    return sum(1 + _count(s.children) for s in spans)
