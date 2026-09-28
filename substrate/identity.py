"""Workload identity. One credential per task, short-lived, revocable.

Agents are principals, not borrowed logins. An agent acting for a person gets
no more than that person holds, and a path can never widen its own scope.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass

from . import config


class IdentityError(Exception):
    pass


@dataclass(frozen=True)
class Credential:
    """A short-lived SVID-style credential bound to one run."""

    svid: str
    spiffe_id: str
    path: str
    entitlements: tuple[str, ...]
    acts_for: str | None
    issued_at: float
    ttl_seconds: int

    @property
    def expired(self) -> bool:
        return time.time() > self.issued_at + self.ttl_seconds

    def __str__(self) -> str:
        return self.spiffe_id


class IdentityProvider:
    """Reads config/spiffe-ids.yaml. One provider for the whole platform."""

    def __init__(self, obs=None) -> None:
        self.obs = obs
        self.doc = config.load_yaml("spiffe-ids.yaml")
        self.trust_domain = self.doc.get("trust_domain", "example.internal")
        self.workloads = {w["path"]: w for w in self.doc.get("workloads", [])}
        self.revoked: set[str] = set()

    def issue(self, path_name: str, acts_for: str | None = None) -> Credential:
        w = self.workloads.get(path_name)
        if w is None:
            raise IdentityError(
                f"no workload identity registered for path {path_name}. "
                f"Add it to config/spiffe-ids.yaml."
            )
        ents = tuple(w.get("entitlements", []))
        if acts_for:
            human = {h["name"]: set(h.get("entitlements", []))
                     for h in self.doc.get("humans", [])}
            held = human.get(acts_for)
            if held is None:
                raise IdentityError(f"unknown principal {acts_for}")
            # An agent acting for a person gets no more than that person holds.
            ents = tuple(e for e in ents if e in held)
        cred = Credential(
            svid=uuid.uuid4().hex[:12],
            spiffe_id=f"spiffe://{self.trust_domain}/agent/{w['name']}",
            path=path_name,
            entitlements=ents,
            acts_for=acts_for,
            issued_at=time.time(),
            ttl_seconds=int(w.get("ttl_seconds", 3600)),
        )
        if self.obs:
            self.obs.record(
                str(cred), "identity.issue", "allowed",
                path=path_name, ttl_seconds=cred.ttl_seconds,
                entitlements=list(ents), acts_for=acts_for,
            )
        return cred

    def verify(self, cred: Credential) -> None:
        if cred.svid in self.revoked:
            raise IdentityError(f"credential {cred.svid} was revoked")
        if cred.expired:
            raise IdentityError(f"credential {cred.svid} expired")

    def revoke(self, cred: Credential) -> None:
        self.revoked.add(cred.svid)
        if self.obs:
            self.obs.record(str(cred), "identity.revoke", "allowed", svid=cred.svid)
