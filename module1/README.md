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

You will see the ten pillars, the config file that backs each one, the module
that builds it, and the platform's spend ceiling.

## Your task

A cost cap looks like something a path owner should set, and an iteration
ceiling looks like a platform concern. The repo puts them the other way round,
and you can see why by trying to widen the cost cap from inside a path.

Open `config/orchestrator.yaml` and set `cost_budget_usd` under `bounds` to
`9.00`. The platform ceiling in `config/budget-policy.yaml` is `2.00`. Run
`python3 module1/run.py` again. The path asked for $9.00 and was granted
$2.00, and the clamp is written to the audit ledger with the reason.

Nothing errored and nothing refused to start. The platform reduced the request
to what the envelope allows and recorded that it did. The iteration ceiling has
no such file, because a path that takes more turns costs its own owner and
nobody else. Blast radius decides the authority in both cases.

Then set `cost_budget_usd` back to `null`. Module 5 starts with every bound
unset.

## Done when

The run shows the clamp, and `cost_budget_usd` is back to `null`. Module 1 has
no checker, because it builds no pillar.

## What is next

Module 2 builds the first pillar, capability, starting from an IDP that
already works.
