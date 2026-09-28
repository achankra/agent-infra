"""Checks Module 2 tasks."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.lab import Checker  # noqa: E402
from substrate import config  # noqa: E402
from substrate.gateway import ToolGateway  # noqa: E402
from substrate.identity import IdentityProvider  # noqa: E402
from substrate.observability import Observability  # noqa: E402
from substrate.policy import PolicyEngine  # noqa: E402
from substrate.registry import ToolRegistry  # noqa: E402

OP = "telemetry:query"


def main() -> int:
    c = Checker("Module 2: what agents reach into")

    reg = ToolRegistry()
    c.task(1, f"{OP} is in the registry", OP in reg.tools,
           "add it to config/tool-registry.yaml with a system and token_cost")

    granted = OP in reg.entitlements.get("/pr-review", [])
    c.task(2, f"/pr-review is entitled to {OP}", granted,
           "add it under the /pr-review grant in config/entitlement-map.yaml")

    tf = config.read_tf_locals("mcp-gateway.tf")
    enabled = "prometheus" in tf.get("enabled_servers", [])
    c.task(3, "the prometheus MCP server is enabled on the gateway", enabled,
           "add \"prometheus\" to enabled_servers in config/mcp-gateway.tf")

    tiered = OP in PolicyEngine().tiers
    c.task(4, f"{OP} has a tier", tiered,
           "unlisted operations classify dangerous by default; place it in "
           "config/permission-tiers.yaml")

    called = False
    detail = ""
    if granted and enabled and tiered:
        obs = Observability()
        ids, pol = IdentityProvider(obs), PolicyEngine(obs)
        # The pre-provisioned identity must also carry the entitlement.
        gw = ToolGateway(reg, pol, obs)
        try:
            cred = ids.issue("/pr-review")
            call = gw.call(cred, OP, payload="up")
            called, detail = call.ok, call.reason
        except Exception as e:
            detail = str(e)
    c.task(5, "an agent can actually call it end to end", called,
           detail or "finish tasks 1 to 4 first. If they pass and this does "
                     "not, the identity in config/spiffe-ids.yaml is missing "
                     "the entitlement.")
    return c.report()


if __name__ == "__main__":
    raise SystemExit(main())
