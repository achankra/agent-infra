# Module 3: Governance

This module builds three pillars: identity, agent security and agent
observability.

Governance is built once and enforced on every path, so all three pillars are
covered together here.

## Workload identity for agents

Each agent run gets its own credential, its own scope and its own budget.

```
   borrowed login                     workload identity

   agent uses a service account       one credential per task
   shared across runs and paths       short-lived, rotated automatically
   scope is whatever the account      scope is explicit and least-privilege
     happens to hold                  declared before the run, enforced
   attribution stops at the account     during it
                                      attribution survives forever
```

An agent acting for a person gets no more than that person holds. Run the
runner with `--acts-for intern@acme.internal` and watch the entitlement set
shrink.

## Classifying operations into tiers

Operations fall into three bands. In the safe band, the agent decides and
executes. In the moderate band, a human approves and the agent executes. In the
dangerous band, a human decides. The same split appears in config terms as an
override pyramid, with flexible defaults, governed overrides that carry a
justification and an expiry, and blocked configurations. See REFERENCES.md.

In this repo, the three bands live in a file.

```
   SAFE          read-only, no lasting effect        allow
   MODERATE      writes something a human reads      allow, recorded
   DANGEROUS     changes production or ownership     deny, or route to a human

   anything unlisted -> dangerous, by omission
```

The tier of each operation is set in config and reviewed like any other policy
change. It is not hardcoded in the agent or decided at runtime.

The classifier is a set of rules. If a model judged how risky an action is, the
agent could argue its way into a lower tier and the gate would stop working.
Reference implementations enforce policy in under a millisecond, which
inference cannot match.

## Extending the policy gate to agents

Two of the three checks already exist in your IDP, and a team that runs
policy-as-code will recognize them. The third is new.

| Check | IDP ancestor | What changes for an agent |
|---|---|---|
| action against policy | yes, policy already gates plans, manifests and charts | the subject is a non-human principal proposing an action mid-task at machine speed, not a pipeline admitting a declarative artifact. The engine is the same; the call site is new. |
| input for injection | none | new. A deterministic pipeline never had to screen inbound content for instructions, because it does not take instructions from data. |
| output and destination | half. Secret scanning and per-zone egress exist | scanning generated content at action time rather than committed code at merge time. Egress binds to an agent identity, not a zone. |

The two rows with an ancestor are where teams go wrong. An identity-bound
egress rule looks like an ordinary egress rule until an agent inherits a zone
it should not have.

```
   proposed action
        |
        v
   [ check 1: action against policy ]  --deny-->  recorded, stopped
        |
        v
   [ check 2: is the input carrying instructions ]  --deny-->  recorded, stopped
        |
        v
   [ check 3: output content and destination ]  --deny-->  recorded, stopped
        |
        v
   execute
```

## The audit ledger

The ledger records every action and every platform decision against an
identity. Cost is attributed per path, per user and per team.

Weak identity is the failure that leaves the least evidence. If agents share a
credential, you cannot attribute what happened, so there is nothing to build a
postmortem from.

## Run it

```
python3 module3/run.py
python3 module3/run.py --acts-for intern@acme.internal
```

The second command shows delegation narrowing the entitlement set.

## Your tasks

`/validate-change` has no identity of its own yet. It has been borrowing the
`/pr-review` credential, which is the antipattern this module addresses.

**Task 1.** Add a workload block for `/validate-change` in
`config/spiffe-ids.yaml`.

**Task 2.** Give it a TTL of 3600 seconds or less. Each task gets its own credential.

**Task 3.** Entitle it to trigger CI, and do not entitle it to merge. ADR 0007
in `sample_app/docs/adr/` says agents do not merge, and your config should
enforce that.

**Task 4.** Confirm a production deploy is stopped for that identity. If it is
not, the tier map is wrong.

**Task 5.** Open `sample_app/docs/tickets/PLAT-418.md` and read the block
support pasted from a customer email. Then add a pattern to
`injection_patterns` in `config/permission-tiers.yaml` that catches it.

The pattern should catch the payload without matching a legitimate ticket. A
pattern that flags every ticket will be switched off.

**Task 6.** Review `egress_allowlist`. One entry does not belong. An agent that
can post output there can publish anything it was ever given.

**Task 7.** Set audit to immutable with at least a year of retention in
`config/otel-collector.yaml`. It currently ships truncating at 30 days, which
is a common failure.

Then:

```
python3 module3/check.py
```

## Done when

Seven PASS lines, and `python3 module3/run.py` shows the merge attempt stopped
with the reason named and the decision in the audit ledger.
