# Module 1: The substrate that runs paths

This module builds no pillar. It maps the ten pillars and settles the decision
the rest of the course depends on: who owns which parameter.

## Throughput, reliability, and the harness

Throughput and reliability come from the platform. Run one model over one
task set on two harnesses and the score changes: Claude Sonnet 4.5 scores 68%
under SWE-Agent and 34% under HAL Generalist, a 34-point gap with the same
weights on the same tasks. Across a benchmark set, harness variance measures
about twice model variance (arXiv:2605.23950).

The ten pillars fall into three blocks.

```
   GOVERNANCE                    HARNESS                      MODELS
   built once,                   the machinery of one turn,   what agents
   enforced everywhere           configured per path          consume

   identity                      capability                   providers
   agent security                context                      inference endpoints
   agent observability           execution                    model hosting
                                 evaluation
```

## Separating governance from harness

A new path inherits identity, policy and audit without asking. It must declare
its own context, tools, limits and definition of done.

You can test that split in both directions.

```
   adding a path forces you to build a governance control
        -> governance was not built once

   adding a path requires no declaration at all
        -> the harness is not per-path
```

The platform team builds both blocks once. Governance is one identity
provider, one policy engine and one audit ledger. The harness is one
orchestrator, one sandbox pool, one context assembler, one tool gateway and one
eval runner. A new path declares its settings against that shared harness
instead of getting its own.

Since both blocks are shared components, what separates them is who has
authority over each parameter.

```
   GOVERNANCE PARAMETERS              HARNESS PARAMETERS
   granted centrally                  the path owner's choice
   a path cannot widen its own        inside the granted envelope

   identity scope                     context sources
   tier map                           which entitled tools this path uses
   policy rules                       iteration ceiling
   egress allowlist                   rubric
   budget cap                         definition of done
   audit retention

   They nest. Tool selection comes from the entitled set.
   The iteration ceiling sits under the cost cap.
```

## Blast radius and approval authority

```
   change a governance control        change a harness parameter
             |                                   |
   every path is affected             one path is affected
             |                                   |
   the security owner reviews it      that path's team owns it
```

CI works the same way. An organization runs one CI system, and each repo
carries its own pipeline config. Nobody builds a CI system per service.

This also explains the ownership rule. Identity stays out of the path because a
path must never be able to grant itself governance.

## Run it

```
python3 module1/run.py
```

You will see the ten pillars, the config artifact that backs each one, and
which module builds it.

## Your tasks

Open `module1/pillars.yaml`.

**Task 1.** Every pillar has an `owner` field set to TODO. Replace all ten with
`governance`, `harness` or `models`.

**Task 2.** The check verifies that each pillar is in the right block. If you
are unsure, apply the two-direction test above.

**Task 3.** Six parameters at the bottom of the file, each with `authority` set
to TODO. Replace each with `platform` or `path-owner`.

Two of the six are easy to get backwards. A cost cap looks like something a
path owner should set, and an iteration ceiling looks like a platform concern.

The repo takes a position on both. `config/budget-policy.yaml` holds the spend
ceiling, and nothing in a path can raise it. If you set `cost_budget_usd` in
`config/orchestrator.yaml` above the ceiling, the run is clamped to the ceiling
and the clamp is recorded in the ledger. The iteration ceiling has no such
file, because a path that takes more turns costs its own owner and nobody else.
Blast radius decides the authority in both cases.

Then:

```
python3 module1/check.py
```

## Done when

All three tasks report PASS.

## What is next

Module 2 builds the first pillar, capability, starting from an IDP that
already works.
