"""The tool registry and entitlement map. Capability, the harness pillar.

The unit of governance is the operation, not the system. One Layer 1 system
yields many capabilities, each separately entitled and separately tiered.
GitHub is one system and at least four grants.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import config


class RegistryError(Exception):
    pass


@dataclass(frozen=True)
class Tool:
    operation: str          # scm:read, ci:trigger, scm:merge
    system: str             # github, argocd, prometheus
    kind: str               # mcp | skill | api | a2a
    description: str
    token_cost: int         # every definition sits in the context window

    def __str__(self) -> str:
        return self.operation


class ToolRegistry:
    """Reads config/tool-registry.yaml and config/entitlement-map.yaml.

    If it is not in the registry, it cannot be called. Curation is a platform
    job: a small model fails a function-calling benchmark at 46 tools and passes
    it at 19, with
    degradation setting in past roughly 20.
    """

    DEGRADATION_THRESHOLD = 20

    def __init__(self) -> None:
        doc = config.load_yaml("tool-registry.yaml")
        self.tools: dict[str, Tool] = {}
        for t in doc.get("tools", []):
            self.tools[t["operation"]] = Tool(
                operation=t["operation"],
                system=t["system"],
                kind=t.get("kind", "mcp"),
                description=t.get("description", ""),
                token_cost=int(t.get("token_cost", 350)),
            )
        ent = config.load_yaml("entitlement-map.yaml")
        self.entitlements: dict[str, list[str]] = {
            e["path"]: list(e.get("operations", [])) for e in ent.get("grants", [])
        }

    def get(self, operation: str) -> Tool:
        if operation not in self.tools:
            raise RegistryError(
                f"{operation} is not in the registry. Unregistered tools cannot be called."
            )
        return self.tools[operation]

    def for_path(self, path_name: str) -> list[Tool]:
        ops = self.entitlements.get(path_name, [])
        missing = [o for o in ops if o not in self.tools]
        if missing:
            raise RegistryError(
                f"config/entitlement-map.yaml grants {missing} to {path_name}, "
                f"but they are not in config/tool-registry.yaml."
            )
        return [self.tools[o] for o in ops]

    def systems(self) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for t in self.tools.values():
            out.setdefault(t.system, []).append(t.operation)
        return {k: sorted(v) for k, v in sorted(out.items())}

    def context_cost(self, path_name: str) -> int:
        """Tokens spent on tool definitions before any work happens."""
        return sum(t.token_cost for t in self.for_path(path_name))

    def curation_warning(self, path_name: str) -> str | None:
        n = len(self.entitlements.get(path_name, []))
        if n > self.DEGRADATION_THRESHOLD:
            return (f"{path_name} is entitled to {n} tools. Selection accuracy "
                    f"degrades past about {self.DEGRADATION_THRESHOLD}.")
        return None
