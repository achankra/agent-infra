"""/pr-review. Read-only, the lowest-risk way into production.

Firing order, derived from necessity rather than asserted as practice:

    identity  binds first, because context is assembled for a principal
       |
    context   assembled by the platform, not browsed by the agent
       |
    capability checked before a tool fires
       |
    model     routed, then called
       |
    evaluation judges an artifact that now exists

    security wraps every turn; observability spans the whole run.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..context import ContextAssembler
from ..gateway import ToolGateway
from ..identity import IdentityProvider
from ..models import ModelGateway
from ..observability import Observability
from ..policy import PolicyEngine
from ..registry import ToolRegistry

PATH = "/pr-review"


@dataclass
class Result:
    path: str = PATH
    identity: str = ""
    context_sources: list[str] = field(default_factory=list)
    context_tokens: int = 0
    dropped_sources: list[tuple[str, str]] = field(default_factory=list)
    tools_available: list[str] = field(default_factory=list)
    tool_calls: list[tuple[str, bool, str]] = field(default_factory=list)
    model: str = ""
    review: str = ""
    usd: float = 0.0
    blocked: list[str] = field(default_factory=list)


def run(obs: Observability | None = None, *, acts_for: str | None = None,
        simulate: bool = True, attempt_merge: bool = False) -> Result:
    obs = obs or Observability()
    res = Result()

    ids = IdentityProvider(obs)
    policy = PolicyEngine(obs)
    registry = ToolRegistry()
    gateway = ToolGateway(registry, policy, obs)
    ctx = ContextAssembler(obs)
    models = ModelGateway(obs)

    span = obs.span(PATH, "platform")

    # identity binds first
    cred = ids.issue(PATH, acts_for=acts_for)
    ids.verify(cred)
    res.identity = str(cred)

    # context is assembled for that principal
    assembled = ctx.assemble(PATH)
    res.context_sources = assembled.names
    res.context_tokens = assembled.tokens
    res.dropped_sources = assembled.dropped

    # capability: what this identity may reach
    res.tools_available = [t.operation for t in registry.for_path(PATH)]

    # a read, then a comment, both through the gateway
    payload = "\n\n".join(s.content for s in assembled.sources)
    for op in ("scm:read", "adr:search"):
        call = gateway.call(cred, op, payload=payload)
        res.tool_calls.append((op, call.ok, call.reason))
        if not call.ok:
            res.blocked.append(f"{op}: {call.reason}")

    # the model is routed, then called
    spec = models.resolve(PATH)
    res.model = f"{spec.model_id}@{spec.pinned_version}"
    prompt = f"Review this change against team conventions.\n\n{payload}"
    text, _tokens, usd = models.complete(cred, PATH, prompt, simulate=simulate)
    res.usd = usd
    res.review = (
        "reserve() accepts a reservation larger than available stock, which "
        "contradicts ADR 0011 stock invariants. A credential literal is present "
        "in source; read it from the environment instead."
        if simulate else text
    )

    # posting the comment is an action, so it passes the gate with its output
    call = gateway.call(cred, "scm:comment", payload=payload,
                        output=res.review, destination="github.acme.internal")
    res.tool_calls.append(("scm:comment", call.ok, call.reason))
    if not call.ok:
        res.blocked.append(f"scm:comment: {call.reason}")

    if attempt_merge:
        call = gateway.call(cred, "scm:merge", payload=payload)
        res.tool_calls.append(("scm:merge", call.ok, call.reason))
        if not call.ok:
            res.blocked.append(f"scm:merge: {call.reason}")

    obs.end_span()
    span.attributes["tools"] = len(res.tools_available)
    obs.counter("path_runs", path=PATH)
    return res
