"""The model gateway and the provider inventory. The models pillar.

The tool gateway governs what the agent can do. This one governs what it can
think with. Clients authenticate to the gateway, never to providers, so keys
stay brokered and quotas and metering live in one place.
"""
from __future__ import annotations

import hashlib
import importlib
from dataclasses import dataclass

from . import config



class ModelError(Exception):
    pass


@dataclass(frozen=True)
class Provider:
    name: str
    status: str
    trains_on_input: bool
    log_retention_days: int
    owner: str
    api: str = "chat-completions"   # chat-completions | messages
    api_key_env: str = ""
    base_url: str = ""
    sdk: str = ""                   # client package, named in config


@dataclass(frozen=True)
class ModelSpec:
    model_id: str
    provider: str
    pinned_version: str
    hosting: str            # managed | private-tenancy | self-hosted
    data_class: str         # public | internal | confidential
    usd_per_1k_tokens: float


class ModelGateway:
    """Reads config/providers.yaml and config/model-routes.toml.

    Unpinned versions make gate results incomparable across runs, so a spec
    without a pinned version is rejected at load time rather than at run time.
    """

    def __init__(self, obs=None) -> None:
        self.obs = obs
        pdoc = config.load_yaml("providers.yaml")
        self.providers = {
            p["name"]: Provider(
                name=p["name"], status=p.get("status", "unapproved"),
                trains_on_input=bool(p.get("trains_on_input", True)),
                log_retention_days=int(p.get("log_retention_days", 0)),
                owner=p.get("owner", "unowned"),
                api=p.get("api", "chat-completions"),
                api_key_env=p.get("api_key_env", ""),
                base_url=p.get("base_url", ""),
                sdk=p.get("sdk", ""),
            )
            for p in pdoc.get("providers", [])
        }
        self.models: dict[str, ModelSpec] = {}
        for m in pdoc.get("models", []):
            if not m.get("pinned_version"):
                raise ModelError(
                    f"{m.get('id')} has no pinned_version in config/providers.yaml. "
                    f"Unpinned versions make gate results incomparable across runs."
                )
            self.models[m["id"]] = ModelSpec(
                model_id=m["id"], provider=m["provider"],
                pinned_version=m["pinned_version"],
                hosting=m.get("hosting", "managed"),
                data_class=m.get("max_data_class", "internal"),
                usd_per_1k_tokens=float(m.get("usd_per_1k_tokens", 0.003)),
            )
        routes = config.load_toml("model-routes.toml")
        self.default = routes.get("routing", {}).get("default")
        self.fallback = routes.get("routing", {}).get("fallback_on_error")
        self.by_path = routes.get("by_path", {})
        self.quota_tokens = int(routes.get("quota", {}).get("tokens_per_run", 40000))

    def resolve(self, path_name: str, data_class: str = "internal") -> ModelSpec:
        model_id = self.by_path.get(path_name, {}).get("model", self.default)
        if model_id not in self.models:
            raise ModelError(
                f"route for {path_name} points at {model_id}, which is not in "
                f"config/providers.yaml."
            )
        spec = self.models[model_id]
        prov = self.providers.get(spec.provider)
        if prov is None or prov.status != "approved":
            raise ModelError(f"provider {spec.provider} is not approved")
        if _rank(data_class) > _rank(spec.data_class):
            raise ModelError(
                f"{path_name} handles {data_class} data; {model_id} is approved "
                f"only up to {spec.data_class}. Route it to a private-tenancy model."
            )
        return spec

    def complete(self, cred, path_name: str, prompt: str, *,
                 data_class: str = "internal", simulate: bool = True) -> tuple[str, int, float]:
        """Returns (text, tokens, usd). Simulate is deterministic so labs repeat."""
        spec = self.resolve(path_name, data_class)
        tokens = max(50, len(prompt) // 4)
        if tokens > self.quota_tokens:
            raise ModelError(
                f"quota exceeded: {tokens} tokens requested, "
                f"{self.quota_tokens} allowed per run"
            )
        usd = round(tokens / 1000 * spec.usd_per_1k_tokens, 6)
        if self.obs:
            self.obs.counter("model_calls", model=spec.model_id, path=path_name)
            self.obs.counter("model_tokens", tokens, model=spec.model_id)
            self.obs.spend(path_name, usd)
            self.obs.record(str(cred), "model.complete", "allow",
                            model=spec.model_id, version=spec.pinned_version,
                            tokens=tokens, usd=usd)
        if simulate:
            digest = hashlib.sha256(prompt.encode()).hexdigest()[:8]
            text = (f"[{spec.model_id}@{spec.pinned_version} simulate:{digest}] "
                    f"reviewed {tokens} tokens of context")
        else:
            text = self._live(spec, prompt)
        return text, tokens, usd

    def _live(self, spec: ModelSpec, prompt: str) -> str:
        """Call the provider named in config, not one hardcoded here.

        Which vendor a path talks to is a routing decision, so it belongs in
        config/providers.yaml with everything else. The gateway knows two
        wire formats and nothing about who is on the other end. Adding a
        vendor is a config entry and, at most, one branch here.
        """
        import os

        prov = self.providers.get(spec.provider)
        if prov is None:
            raise ModelError(f"{spec.provider} is not in config/providers.yaml")
        if not prov.api_key_env:
            raise ModelError(
                f"{prov.name} has no api_key_env in config/providers.yaml, "
                f"so the gateway cannot broker a credential for it")
        key = os.environ.get(prov.api_key_env)
        if not key:
            raise ModelError(
                f"{prov.api_key_env} is not set. Export it, or drop --live "
                f"and run in simulate mode")

        if prov.api not in ("messages", "chat-completions"):
            raise ModelError(
                f"{prov.name} declares api: {prov.api}, which the gateway "
                f"does not speak. Use messages or chat-completions")
        if not prov.sdk:
            raise ModelError(
                f"{prov.name} has no sdk in config/providers.yaml. Name the "
                f"client package there so this file never has to know it")
        mod = importlib.import_module(prov.sdk)

        if prov.api == "messages":
            client = mod.Client(api_key=key, base_url=prov.base_url or None)
            reply = client.messages.create(
                model=spec.pinned_version, max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            return reply.content[0].text

        client = mod.Client(api_key=key, base_url=prov.base_url or None)
        reply = client.chat.completions.create(
            model=spec.pinned_version, max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return reply.choices[0].message.content

        raise ModelError(
            f"{prov.name} declares api: {prov.api}, which the gateway does "
            f"not speak. Use chat-completions or messages")


def _rank(data_class: str) -> int:
    return {"public": 0, "internal": 1, "confidential": 2}.get(data_class, 2)
