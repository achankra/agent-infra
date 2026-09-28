"""The permission surface and the gate. Governance, built once.

Three tiers, not a binary switch: Safe, Moderate, Dangerous. Tier assignment is
reviewed config, and the classifier that maps an action to a tier is rules, not
a model call. If a model judges how risky an action is, the agent can talk its
way into a lower tier and the gate is no longer a gate.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from . import config


class Tier(str, Enum):
    SAFE = "safe"
    MODERATE = "moderate"
    DANGEROUS = "dangerous"


class Decision(str, Enum):
    ALLOW = "allow"
    REVIEW = "review"
    DENY = "deny"


@dataclass
class Verdict:
    decision: Decision
    tier: Tier
    reason: str
    check: str

    @property
    def allowed(self) -> bool:
        return self.decision is Decision.ALLOW


class PolicyEngine:
    """Reads config/permission-tiers.yaml. Deterministic by construction.

    Three checks run in order. Two have an IDP ancestor, one does not:
        action  - policy on the proposed action        (OPA already does this)
        input   - injection screening on inbound data  (new)
        output  - scanning and egress at action time   (half exists today)
    """

    def __init__(self, obs=None) -> None:
        self.obs = obs
        doc = config.load_yaml("permission-tiers.yaml")
        self.tiers: dict[str, Tier] = {}
        for tier_name, ops in (doc.get("tiers") or {}).items():
            for op in ops or []:
                self.tiers[op] = Tier(tier_name)
        self.rules = doc.get("rules", {})
        self.injection_patterns = [
            re.compile(p, re.I) for p in doc.get("injection_patterns", [])
        ]
        self.output_patterns = [
            (name, re.compile(p)) for name, p in (doc.get("output_patterns") or {}).items()
        ]
        self.egress_allowlist = set(doc.get("egress_allowlist", []))

    # -- classification ------------------------------------------------
    def classify(self, operation: str) -> Tier:
        """Deterministic classifier. Unlisted operations are Dangerous by default."""
        return self.tiers.get(operation, Tier.DANGEROUS)

    # -- check 1: action against policy --------------------------------
    def check_action(self, cred, operation: str) -> Verdict:
        tier = self.classify(operation)
        rule = (self.rules.get(tier.value) or {}).get("decision", "deny")
        entitled = operation in cred.entitlements

        # The tier is the platform's rule about the operation itself, so it is
        # reported first. Entitlement is the narrower per-path grant.
        if rule == "deny":
            extra = "" if entitled else " and is not entitled to this path"
            return Verdict(Decision.DENY, tier,
                           f"{operation} is classified {tier.value}{extra}",
                           "action")
        if not entitled:
            return Verdict(Decision.DENY, tier,
                           f"{operation} is {tier.value} but is not in the "
                           f"entitlements for {cred.path}",
                           "action")
        if rule == "allow":
            return Verdict(Decision.ALLOW, tier, f"{operation} is {tier.value}", "action")
        if rule == "review":
            return Verdict(Decision.REVIEW, tier,
                           f"{operation} is {tier.value} and needs human approval", "action")
        return Verdict(Decision.DENY, tier,
                       f"{operation} is {tier.value} and is denied by policy", "action")

    # -- check 2: input as attack surface ------------------------------
    def check_input(self, text: str) -> Verdict:
        for pat in self.injection_patterns:
            m = pat.search(text or "")
            if m:
                return Verdict(Decision.DENY, Tier.DANGEROUS,
                               f"inbound content matched injection pattern: {m.group(0)[:60]}",
                               "input")
        return Verdict(Decision.ALLOW, Tier.SAFE, "no injection pattern matched", "input")

    # -- check 3: output and destination -------------------------------
    def check_output(self, text: str, destination: str | None = None) -> Verdict:
        for name, pat in self.output_patterns:
            m = pat.search(text or "")
            if m:
                return Verdict(Decision.DENY, Tier.DANGEROUS,
                               f"output matched {name}", "output")
        if destination and destination not in self.egress_allowlist:
            return Verdict(Decision.DENY, Tier.DANGEROUS,
                           f"egress to {destination} is not allowlisted for this identity",
                           "output")
        return Verdict(Decision.ALLOW, Tier.SAFE, "output clean", "output")

    # -- the gate ------------------------------------------------------
    def gate(self, cred, operation: str, *, payload: str = "",
             output: str = "", destination: str | None = None) -> Verdict:
        for verdict in (
            self.check_input(payload),
            self.check_action(cred, operation),
            self.check_output(output, destination),
        ):
            if not verdict.allowed:
                if self.obs:
                    self.obs.record(str(cred), operation, verdict.decision.value,
                                    tier=verdict.tier.value, check=verdict.check,
                                    reason=verdict.reason)
                    self.obs.counter("governance_denials", check=verdict.check,
                                     tier=verdict.tier.value)
                return verdict
        ok = Verdict(Decision.ALLOW, self.classify(operation), "all three checks passed", "gate")
        if self.obs:
            self.obs.record(str(cred), operation, "allow", tier=ok.tier.value, check="gate")
        return ok
