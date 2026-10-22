# Module 8: The Future of Platform Engineering

This module builds no new pillar. It points the same substrate at work that has
nothing to do with software.

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

   Only the parameters change between them.
```

Platform engineers own the substrate and domain teams own the workflows. The
published agent adoption maturity models assume that division, and it is why
the rollout is staged rather than done all at once.

## The status of this claim

Agents already span functions, but through separate platforms. The agent
platforms sold into IT, HR, finance and other functions are separate products,
each with its own identity model, its own audit trail and its own bill. I have
not found a documented case of one organization reusing the same engineering
pillars across them.

The case for a single substrate is therefore the course's position, argued from
that fragmentation. It is not a description of existing practice.

## The measured comparison

With the same model and the same task set, Claude Sonnet 4.5 scores 68% under
SWE-Agent and 34% under HAL Generalist (arXiv:2605.23950).

One scaffold is built for software engineering. The other is general purpose
and used unchanged across benchmarks. Because both ran the same model over the
same tasks, the gap comes from the harness. The figures are published, so you
can cite them instead of running a freeze-and-measure experiment of your own.

## What leadership asks for

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

The runner shows the software paths and any non-software workloads declared
against the same pillars.

## Your tasks

Finance wants ledger reconciliation run by an agent. You are the platform team
and they are the domain team, so your job is to hand them a manifest. You are
not starting a project of your own.

Open `config/workload-manifests/finance-reconciliation.yaml`.

**Task 1.** Name the domain owner. Pick someone in finance, since they own the
workflow and you own the substrate.

**Task 2.** Set a TTL of 3600 seconds or less. The rule is the same for a
finance workload.

**Task 3.** Write at least two entitlements as operations rather than systems,
the way the software paths use `scm:read` instead of `github`.
Reconciliation might need `ledger:read` and `ledger:post`. Reading a ledger
and posting to one carry different risk, which is why entitlements are written
per operation.

**Task 4.** Declare the data class. Financial ledger data is rarely internal,
and the model gateway will refuse a route that exceeds what the model is
approved for.

**Task 5.** Grant a control mode. Reconciliation that posts to a ledger is more
than assistive work, and it should not start at bounded autonomy either.

**Task 6.** Bound the loop with an iteration cap and a cost budget. Every loop
needs a way to stop, whatever domain it serves.

**Task 7.** Define done, and route a low score to a person. Reconciliation has
a clear deterministic gate available, since the ledger either balances or it
does not, so use that as the definition of done.

**Task 8.** Set a cost per workflow target. Leadership reviews spend at the
workflow level, so this is the figure you will be asked for.

**Task 9.** Confirm you did not need a fourth permission tier. If a finance
workload needed one, the tier map was specific to software.

Then:

```
python3 module8/check.py
python3 module8/run.py
```

## Discussion

Go back through the fields you filled in and sort them into those specific to
finance and those that repeat decisions you made for `/pr-review` with
different values. That ratio measures the reuse argument against your own
work.

Then decide who in your organization would own this manifest and who would
review it. If nobody can answer that, the gap is organizational, and it belongs
on your roadmap ahead of any tooling.

## Done when

Nine PASS lines, and a finance workload running on a substrate built for
software delivery, with no new pillars.
