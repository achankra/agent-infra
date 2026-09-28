# References

Where each pillar's design came from. Chapter-level, so you can go to the
long version.

## Governance

Identity, least privilege by persona, and the escape hatch as temporary
privilege escalation with logging, auditing and reversion:
*The Platform Engineer's Handbook*, Ch 3.

Permission tiers. Ch 14, Table 14.2 classifies agent actions as safe (agent
decides, agent executes), medium (agent proposes, human approves) and high
(human decides, human executes). `config/permission-tiers.yaml` is that table.

The same three bands from the config side, as an override pyramid of flexible
defaults, governed overrides carrying justification and an expiry, and blocked
configurations: *Domain-Driven Platform Engineering*, Ch 6.

Policy as code as enforcement gates, and the separation of platform-user
identity from cloud infrastructure identity: *Effective Platform Engineering*,
Ch 4. Rego and Gatekeeper: *The Platform Engineer's Handbook*, Ch 11.

Audit and attribution: *Effective Platform Engineering*, Ch 5.

## Harness

Capability as governed exposure rather than system access. *Effective Platform
Engineering*, Ch 4: infrastructure is provisioned by the platform on the team's
behalf rather than by granting the team permissions to do it themselves. The
same rule, with an agent in the team's place, is `config/entitlement-map.yaml`.

Domain defaults, which encode a regulatory requirement once so no individual
has to understand the nuance: *Domain-Driven Platform Engineering*, Ch 6. That
is what `config/data-contracts/` implements.

The control plane the substrate is modeled on: *Effective Platform
Engineering*, Ch 7.

Operating metrics in `config/agent-slos.yaml`: *The Platform Engineer's
Handbook*, Ch 14, Table 14.3.

Confidence gating ahead of autonomous execution: same chapter.

## Claims with external sources

Harness variance against model variance, and the 68% / 34% figure for one
model across two harnesses: arXiv:2605.23950.

Tool count and selection accuracy: arXiv:2411.15399. Note the scope, which is
a quantized 8B model on edge hardware, not a frontier model.

Position of a fact within the context window: arXiv:2307.03172.

Judge reliability: arXiv:2606.19544, and RAND's harness at arXiv:2603.05399.

Long-horizon completion against human task time: arXiv:2606.29537.

Agents as workloads, and static API keys as an anti-pattern for agent
identity: IETF draft-ietf-wimse-aims.

AI spend management among FinOps practitioners: State of FinOps 2026.

## Course context

The paths-to-outcome model and its enterprise extension of identity, policy
and state: von Grunberg and Galante, *Thinking in Platforms*, Weave
Intelligence, 2026.

The four maturity levels taught in Course 2: Galante, von Grunberg, Haigh and
Chankramath, *The four levels of agentic software development in the
enterprise*, Weave Intelligence, 2026.

## Books cited above

Chankramath, Cheneweth, Oliver and Alvarez. *Effective Platform Engineering*.
Manning, 2026.

Chankramath and Gibson. *The Platform Engineer's Handbook*. Packt, 2026.

Chankramath and Ryan. *Domain-Driven Platform Engineering*. Apress, 2026.
