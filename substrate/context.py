"""Context assembly. What you hand the agent, and what it assumes because you didn't.

The context window exists per turn. It is not memory. Quality falls as the
window fills and with where a fact sits in it, so compaction runs before the
window degrades rather than after.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from . import config

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Source:
    name: str
    kind: str            # knowledge | live | memory
    retrieval: str       # rag | mcp | file
    certified: bool
    owner: str
    content: str = ""
    tokens: int = 0
    quarantined: int = 0   # spans redacted because they carried instructions


@dataclass
class Assembled:
    sources: list[Source] = field(default_factory=list)
    dropped: list[tuple[str, str]] = field(default_factory=list)
    compacted: bool = False

    @property
    def quarantined(self) -> int:
        return sum(s.quarantined for s in self.sources)

    @property
    def tokens(self) -> int:
        return sum(s.tokens for s in self.sources)

    @property
    def names(self) -> list[str]:
        return [s.name for s in self.sources]


class ContextAssembler:
    """Reads config/rag-config.toml and config/data-contracts/.

    Governed sources only: certified, contracted, owned. A source without a
    data contract is not assembled, it is reported.
    """

    def __init__(self, obs=None, policy=None) -> None:
        self.obs = obs
        # Screening happens where untrusted content enters the window. Doing it
        # here rather than on every tool call means one poisoned source is
        # neutralised instead of killing the whole run.
        if policy is None:
            from .policy import PolicyEngine
            policy = PolicyEngine(obs)
        self.policy = policy
        self.cfg = config.load_toml("rag-config.toml")
        self.window = int(self.cfg.get("window", {}).get("max_tokens", 8000))
        self.compact_at = float(self.cfg.get("window", {}).get("compact_at_fraction", 0.6))
        self.require_contract = bool(
            self.cfg.get("governance", {}).get("require_data_contract", True)
        )
        self.contracts = self._load_contracts()

    def _load_contracts(self) -> dict[str, dict]:
        d = config.CONFIG / "data-contracts"
        out = {}
        if d.exists():
            for f in sorted(d.glob("*.yaml")):
                doc = config.load_yaml(f"data-contracts/{f.name}")
                out[doc.get("source", f.stem)] = doc
        return out

    def assemble(self, path_name: str) -> Assembled:
        wanted = self.cfg.get("paths", {}).get(path_name, {}).get("sources", [])
        result = Assembled()
        for name in wanted:
            spec = self.cfg.get("sources", {}).get(name)
            if spec is None:
                result.dropped.append((name, "no source definition in rag-config.toml"))
                continue
            contract = self.contracts.get(name)
            if self.require_contract and contract is None:
                result.dropped.append((name, "no data contract in config/data-contracts/"))
                continue
            content, redacted = self._quarantine(self._read(spec), name)
            src = Source(
                name=name,
                kind=spec.get("kind", "knowledge"),
                retrieval=spec.get("retrieval", "file"),
                certified=bool(contract and contract.get("certified")),
                owner=(contract or {}).get("owner", "unowned"),
                content=content,
                tokens=_tok(content),
                quarantined=redacted,
            )
            if self.require_contract and not src.certified:
                result.dropped.append((name, "data contract is not certified"))
                continue
            result.sources.append(src)

        budget = int(self.window * self.compact_at)
        if result.tokens > budget:
            result.compacted = True
            self._compact(result, budget)
        if self.obs:
            self.obs.gauge("context_tokens", result.tokens, path=path_name)
            self.obs.counter("context_sources", len(result.sources), path=path_name)
            for name, why in result.dropped:
                self.obs.record("platform", "context.drop", "deny", source=name, reason=why)
        return result

    def _quarantine(self, text: str, name: str) -> tuple[str, int]:
        """Redact spans that carry instructions. A ticket is data; an
        instruction inside one is not an instruction."""
        redacted = 0
        for pat in self.policy.injection_patterns:
            text, n = pat.subn("[redacted: instruction found in data]", text)
            redacted += n
        if redacted and self.obs:
            self.obs.counter("context_quarantined", source=name)
            self.obs.record("platform", "context.quarantine", "redacted",
                            source=name, spans=redacted)
        return text, redacted

    def _compact(self, result: Assembled, budget: int) -> None:
        """Compact before the window degrades. A summary written after rot has
        set in is itself degraded, because the model producing it is impaired."""
        for s in result.sources:
            if result.tokens <= budget:
                break
            keep = max(200, int(len(s.content) * 0.4))
            s.content = s.content[:keep] + "\n... [compacted]"
            s.tokens = _tok(s.content)

    def _read(self, spec: dict) -> str:
        p = spec.get("path")
        if not p:
            return spec.get("inline", "")
        f = ROOT / p
        if f.is_dir():
            parts = []
            for x in sorted(f.rglob("*")):
                if x.is_file() and x.suffix in (".py", ".md", ".yaml", ".toml", ".txt"):
                    parts.append(x.read_text())
            return "\n\n".join(parts)
        return f.read_text() if f.exists() else ""


def _tok(text: str) -> int:
    """Rough token count. Four characters per token is close enough for a lab."""
    return max(1, len(text) // 4)
