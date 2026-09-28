# Module 7: The Full-Path Build

This module runs for 45 minutes and is the capstone. It introduces no new
pillar, and instead takes one path through every pillar already built.

## Pillar firing order

The order is not documented publicly, because harness orchestration is
proprietary at every major vendor. It is derived here from necessity instead.

```
   identity  ---> context ---> capability ---> model ---> evaluation
      |             |             |              |            |
   binds first,  assembled     checked        routed,      judges an
   because       for a         before a       then         artifact that
   context is    principal     tool fires     called       now exists
   assembled
   for a
   principal

   security wraps every turn.      observability spans the whole run.
```

Each step needs the one before it. Context cannot be assembled until you know
who it is for. A tool cannot be checked until you know which tools are in play.
An artifact cannot be judged until it exists.

## What breaks when a pillar is missing

Silent failures have three layers: a trigger, the external event that starts
it; an amplifier, the architectural flaw that spreads it; and a concealer, the
absence that hides it until a person notices. A fix that addresses only the
trigger is cosmetic, because triggers are unbounded while amplifiers and
concealers are finite and belong to your architecture.

The worked case is the evaluation vendor breach from Module 5. Trigger: a cloud
account holding customer API keys was accessed. Amplifier: customers had handed
their provider keys to that vendor to store, so one account held many.
Concealer: the keys still worked and nothing in the customer's own platform
changed, so detection came from provider usage spikes rather than from any
alert they owned.

Three-layer model from Wu, arXiv:2606.14589, a study of 22 incidents in a
single production agent runtime between April and June 2026. One system, one
author: the structure travels, the frequencies do not.

Identity is the exception worth naming. Its failure mode produces no
postmortem, because the failure is the inability to attribute.

| Pillar removed | What you see |
|---|---|
| identity | the run works, and you cannot say who did it |
| capability | the tool call is refused at the registry |
| gateway | the operation exists and the server is unreachable |
| context | the source is dropped and reported, and the review is generic |
| models | the route resolves to an unapproved provider and the run stops |
| execution | the loop does not stop |
| evaluation | everything promotes |

## Choosing the first control mode

`/pr-review` is the lowest-risk way into production, and the pattern is live in
production products in 2026. It reads, it comments, it cannot merge. Start
there, then earn the next control mode with evidence.

## Run it

```
python3 module7/run.py
```

Both paths, end to end, with every pillar named as it fires.

## Your tasks

The capstone is a third path. On-call wants `/oncall-triage`: an agent that
reads telemetry when an alert fires, searches decision records and incident
history, and posts a triage summary. It may not deploy and it may not merge.

You will not write any Python. If the substrate is right, a new path is a
manifest.

**Tasks 1 to 3.** Confirm the substrate is complete. Identities for both
shipped paths, all three stops set, a rubric for each path. These come from
Modules 3, 5 and 6. If any of them fail, go back.

**Task 4.** `/pr-review` still completes and its merge attempt is still
stopped.

**Task 5.** `/validate-change` still converges and promotes.

**Task 6.** Declare `/oncall-triage` across the harness. Six files:

```
   spiffe-ids.yaml        identity, TTL, entitlements
   entitlement-map.yaml   which operations
   rag-config.toml        which sources, and a path entry
   model-routes.toml      which model
   orchestrator.yaml      a control mode
   eval-rubrics/          a rubric with bands
```

Give it `telemetry:query` from Module 2 and `adr:search`. Do not give it
`deploy:production` or `scm:merge`.

**Task 7.** You should not have touched the governance structure. The tier map
may gain operations; it must still have three tiers and three rules. If adding
a path forced you to build a governance control, governance was not built once.

**Task 8.** The path can be issued an identity and run.

Then:

```
python3 module7/check.py
python3 module7/run.py
```

## Discussion

Now break one pillar on purpose and rerun. The runner lists how to break each
one. Pick identity, remove the workload block, and notice what the failure
looks like: not an error, just a run you can no longer attribute.

Put it back before you move on.

## Done when

Eight PASS lines, and a third path running on a substrate you did not modify to
accommodate it.
