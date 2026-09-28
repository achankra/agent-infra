# Module 1: The substrate that runs paths

This module runs for 45 minutes and builds no pillar. It is the map of the
ten pillars, and it settles the one decision the rest of the course depends
on, which is who owns which parameter.

## Throughput, reliability, and the harness

Throughput and reliability come from the platform, not the model. Run one
model over one task set on two harnesses and the number moves: Claude Sonnet
4.5 scores 68% under SWE-Agent and 34% under HAL Generalist. Same weights,
same tasks, 34 points. Across a benchmark set, harness variance measures about
twice model variance (arXiv:2605.23950).

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

That is testable in both directions.

```
   adding a path forces you to build a governance control
        -> governance was not built once

   adding a path requires no declaration at all
        -> the harness is not per-path
```

Both blocks are built once, by the platform team. One identity provider, one policy engine,
one audit ledger, and equally one orchestrator, one sandbox pool, one context
assembler, one tool gateway, one eval runner. A new path does not get a new
harness. It gets a manifest.

What separates the two is authority over the parameter, not whether the
component exists.

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

You already live this: one CI system, per-repo pipeline config. Nobody builds a
CI system per service.

This also sharpens the ownership rule. The reason not to build identity inside
a path is not that governance is built once. It is that a path must never be
able to grant itself governance.

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

**Task 2.** Getting them in the right block is the check. If you are unsure,
apply the two-direction test above.

**Task 3.** Six parameters at the bottom of the file, each with `authority` set
to TODO. Replace each with `platform` or `path-owner`.

Two of the six are worth arguing about in the session. A cost cap looks like
something a path owner should set, and an iteration ceiling looks like a
platform concern. Work out which way round they go and why.

The repo takes a position on this, so you can check your answer against it
rather than against me. `config/budget-policy.yaml` holds the spend ceiling
and nothing in a path can raise it: set `cost_budget_usd` in
`config/orchestrator.yaml` above the ceiling and the run is clamped to the
ceiling and the clamp is recorded in the ledger. The iteration ceiling has no
such file, because a path taking more turns costs its own owner and nobody
else. That is blast radius deciding authority, and it is the whole of the
argument.

Then:

```
python3 module1/check.py
```

## Done when

All three tasks report PASS.

## What is next

Module 2 builds the first pillar, capability, and it starts by handing you an
IDP that already works.
