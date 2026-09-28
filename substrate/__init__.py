"""Shared agent infrastructure. Built once by the platform team.

Every module in this course adds configuration to config/, never a new copy of
this package. That split is the course's central claim: governance and the
harness are platform-built once and parameterized per path.
"""
__all__ = [
    "config", "identity", "policy", "registry", "gateway", "context",
    "orchestrator", "models", "evaluation", "observability",
]
