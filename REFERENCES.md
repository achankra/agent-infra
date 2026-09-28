# Where this comes from

Course 3 is not a new argument. It is the platform-engineering argument I have
been making in three books, pointed at a non-human principal. This file records
which idea came from where, so you can go and read the long version.

## My own books

**Chankramath, A., Cheneweth, N., Oliver, B., Alvarez, S.**
*Effective Platform Engineering.* Manning, 2026. ISBN 9781633436497.

- Ch 4, Governance, compliance, and trust. Policy as code as enforcement gates,
  and the identity separation this course leans on: "Infrastructure available
  through the platform is provisioned by the platform on the development team's
  behalf rather than merely granting the team permissions to do it themselves."
  That sentence is Module 2's whole argument about exposing operations rather
  than systems, written three years before anyone needed it for agents.
- Ch 7, Platform control plane foundations. The substrate this course calls
  Layer 3 is a control plane. Same shape, new tenant.
- Ch 5, Evolutionary observability. Module 3's audit ledger.

**Chankramath, A., Gibson, A.**
*The Platform Engineer's Handbook.* Packt, 2026.

- Ch 3, Securing Platform Access. Least privilege by persona, and the escape
  hatch as "temporary privilege escalation with the right amount of automated
  logging, auditing, and reverting." Module 3's delegation rule and the
  envelope-widening route both come from here. The CI/CD pipeline running on
  one cluster-admin service account is the antipattern Module 3 opens on.
- Ch 11, Validating Compliance and Policy as Code. Rego, Gatekeeper, and the
  point that a policy everyone exempts is either badly designed or badly
  explained.
- Ch 14, Agentic and AI-Augmented Platforms. Table 14.2 classifies agent
  actions as safe (agent decides, agent executes), medium (agent proposes,
  human approves), and high (human decides, human executes). Module 3's three
  permission tiers are that table, as config. Table 14.3 gives the six
  operating metrics in `config/agent-slos.yaml`.

**Chankramath, A., Ryan, E.**
*Domain-Driven Platform Engineering.* Apress, 2026.
ISBN 979-8-8688-2760-0. doi:10.1007/979-8-8688-2761-7

- Ch 6, Golden Paths and API Design per Domain. The override pyramid: flexible
  defaults a developer changes freely, governed overrides that require
  justification and carry an expiry, and blocked configurations that cannot be
  overridden regardless of justification. `config/permission-tiers.yaml` is
  that pyramid with a different subject.
- Ch 6 also carries the domain defaults idea that `config/data-contracts/`
  implements: encode the regulatory requirement once so no developer has to
  understand the nuance.
- Ch 10, GenAI and Autonomous Platforms.

## Not my book

**von Grunberg, K., Galante, L.** *Thinking in Platforms.* Weave
Intelligence, 2026. ISBN 978-3-9828877-0-8.

The paths-to-outcome model, and the enterprise extension of identity, policy
and state. Course 3 builds that extension for agents. Cited on the slides by
its authors, not by me.

**Galante, L., von Grunberg, K., Haigh, M., Chankramath, A.**
*The four levels of agentic software development in the enterprise.*
Weave Intelligence, 2026.

The maturity model Course 2 teaches. I am one of four authors.
