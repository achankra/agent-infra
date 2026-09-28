# ADR 0007: Agents do not merge

Status: accepted
Date: 2026-03-11
Owner: platform-eng

## Context

Agent-authored changes reach the same pipeline as human-authored ones. The
question is whether an agent may complete the merge itself once gates pass.

## Decision

Agents may read, comment and trigger. Merge stays a human action at Level 2.
The merge operation is classified dangerous in the permission surface, so the
decision is enforced by config rather than by convention.

## Consequences

Review capacity remains the constraint at Level 2. That is accepted, because
the alternative is an unattributable production change.
