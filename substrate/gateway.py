"""The tool gateway. One doorway, so authz, limits and audit live in one place.

This gateway governs what an agent can do. The model gateway in models.py
governs what it can think with. Same pattern, different subject.

    without a gateway                 with a gateway
    agent -> github                   agent ---\
    agent -> argocd                   agent ----> [gateway] -> github
    agent -> prometheus               agent ---/   authz       argocd
    N integrations, N authz points                 limits      prometheus
                                                   audit
"""
from __future__ import annotations

import time
from dataclasses import dataclass

from . import config
from .policy import Decision, PolicyEngine
from .registry import ToolRegistry


class GatewayError(Exception):
    pass


@dataclass
class Call:
    operation: str
    ok: bool
    reason: str
    result: str | None = None
    tier: str = ""


class ToolGateway:
    """Reads config/mcp-gateway.tf for rate limits and the enabled server list."""

    def __init__(self, registry: ToolRegistry, policy: PolicyEngine, obs=None) -> None:
        self.registry = registry
        self.policy = policy
        self.obs = obs
        tf = config.read_tf_locals("mcp-gateway.tf")
        self.rate_limit = int(tf.get("rate_limit_per_minute", 30))
        self.enabled_servers = set(tf.get("enabled_servers", []))
        self.audit_enabled = bool(tf.get("audit_all_calls", True))
        self._calls: list[float] = []
        self.handlers: dict[str, callable] = {}

    def register_handler(self, operation: str, fn) -> None:
        """Bind an operation to something that actually does work."""
        self.handlers[operation] = fn

    def call(self, cred, operation: str, **kwargs) -> Call:
        # 1. the operation must exist in the registry
        try:
            tool = self.registry.get(operation)
        except Exception as e:
            return Call(operation, False, str(e))

        # 2. its backing server must be enabled on the gateway
        if tool.system not in self.enabled_servers:
            reason = (f"{tool.system} is not in enabled_servers in config/mcp-gateway.tf")
            self._audit(cred, operation, "deny", reason)
            return Call(operation, False, reason)

        # 3. rate limit, enforced by the gateway rather than by each integration
        now = time.time()
        self._calls = [t for t in self._calls if now - t < 60]
        if len(self._calls) >= self.rate_limit:
            reason = f"rate limit of {self.rate_limit}/min exceeded at the gateway"
            self._audit(cred, operation, "deny", reason)
            return Call(operation, False, reason)

        # 4. the gate
        verdict = self.policy.gate(
            cred, operation,
            payload=str(kwargs.get("payload", "")),
            output=str(kwargs.get("output", "")),
            destination=kwargs.get("destination"),
        )
        if verdict.decision is not Decision.ALLOW:
            return Call(operation, False, verdict.reason, tier=verdict.tier.value)

        # 5. execute
        self._calls.append(now)
        handler = self.handlers.get(operation)
        result = handler(**kwargs) if handler else f"{operation} executed"
        if self.obs:
            self.obs.counter("tool_calls", operation=operation, system=tool.system)
        return Call(operation, True, "allowed", result=str(result),
                    tier=verdict.tier.value)

    def _audit(self, cred, operation, decision, reason) -> None:
        if self.obs and self.audit_enabled:
            self.obs.record(str(cred), operation, decision, reason=reason, at="gateway")
            self.obs.counter("governance_denials", check="gateway", tier="n/a")
