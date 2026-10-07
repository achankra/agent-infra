# Module 8: The Future of Platform Engineering

This module runs for 45 minutes and introduces no new pillar. It points the
same substrate at work that has nothing to do with software.

## Agent workloads beyond software delivery

```
   /pr-review          /reconcile-ledger      /campaign-brief     /offer-letter
   software            finance                marketing           HR
        \                   |                      |                  /
         \                  |                      |                 /
          +--------------- the same ten pillars ------------------+
                identity   agent security   agent observability
                capability context   execution   evaluation
                providers  inference endpoints   model hosting

   What changes between them is every parameter, and nothing else.
```

Platform engineers own the substrate and domain teams own the workflows. That
division is the assumption behind the published agent adoption maturity models,
and it is why this is staged rather than a big-bang rollout.

## The status of this claim

Agents do span functions today, but they do it through separate platforms. The
major vendor offerings for IT, HR, finance, legal and procurement are distinct
products, each with its own identity model, its own audit trail and its own
bill. I have not found a documented case of one organization reusing the same
engineering pillars across all of them.

The argument for a single substrate therefore rests on that fragmentation
rather than on anyone's existing practice.

## The measured comparison

Same model, same task set, two harnesses: Claude Sonnet 4.5 scores 68% under
SWE-Agent and 34% under HAL Generalist (arXiv:2605.23950).

One scaffold is built for software engineering and the other is general
purpose and used unchanged across benchmarks. Since both ran the same model
over the same tasks, the gap comes from the harness. The figures are published,
so you can cite them instead of running a freeze-and-measure experiment of your
own.

## What leadership asks for

Leadership asks for two things.

```
   cost per workflow          what leadership asks for. The FinOps Foundation
                              framework still meters cost per token and cost
                              per inference; the workflow number is the one
                              you have to derive

   a maturity roadmap         where you are, what the next level demands,
                              and which path goes first
```

98% of FinOps practitioners now manage AI spend, up 67 points from 31% two
years ago (State of FinOps 2026, n=1,192).

## Run it

```
python3 module8/run.py
```

Shows the software paths and any non-software workloads declared against the
same pillars.

## Your tasks

Finance wants ledger reconciliation run by an agent. You are the platform team
and they are the domain team, so your job is to hand them a manifest rather
than to start a project of your own.

Open `config/workload-manifests/finance-reconciliation.yaml`.

**Task 1.** Name the domain owner. Pick someone in finance, since they own the
workflow and you own the substrate.

**Task 2.** Set a TTL of 3600 seconds or less. The rule does not change because
the workload is finance.

**Task 3.** Write at least two entitlements as operations, not systems. Look at
how the software paths do it: `scm:read`, not `github`. Reconciliation might
need `ledger:read` and `ledger:post`.

Reading a ledger and posting to one carry different risk, which is why
entitlements are written per operation rather than per system.

**Task 4.** Declare the data class. Financial ledger data is rarely internal,
and the model gateway will refuse a route that exceeds what the model is
approved for.

**Task 5.** Grant a control mode. Reconciliation that posts to a ledger is not
assistive work, and it is not bounded autonomy on day one either.

**Task 6.** Bound the loop with an iteration cap and a cost budget, because
every loop needs a way to stop whatever the domain it serves.

**Task 7.** Define done, and route a low score to a person. Reconciliation has
a crisp deterministic gate available to it, since the ledger either balances or
it does not, so write that down as the definition of done.

**Task 8.** Set a cost per workflow target. Leadership reviews spend at the
workflow level, so this is the figure you will be asked for.

**Task 9.** Confirm you did not need a fourth permission tier. A finance
workload that forces one tells you the tier map was software-specific all
along.

Then:

```
python3 module8/check.py
python3 module8/run.py
```

## Discussion

Go back through the fields you just filled in and sort them. Which were
specific to finance, and which were the same decisions you made for
`/pr-review` with different values? The ratio you get is the reuse argument
measured against your own work.

Then work out who in your organization would own this manifest and who would
review it. If nobody can answer that, the gap is organizational rather than
technical, and it belongs on your roadmap ahead of any tooling.

## Done when

Nine PASS lines, and a finance workload running on a substrate built for
software delivery, with no new pillars.
