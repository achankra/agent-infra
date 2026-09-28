# Module 8: The Future of Platform Engineering

45 minutes. No new pillar. The same substrate, pointed somewhere else.

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

Platform engineers own the substrate. Domain teams own the workflows. That
division is the assumption behind the published agent adoption maturity models,
and it is why this is staged rather than a big-bang rollout.

## The status of this claim

Be straight about this in the room. Agents do span functions today, but through
separate platforms: the major vendor offerings for IT, HR, finance, legal and
procurement are distinct products, and cross-domain reuse of engineering
pillars is undocumented.

So the argument for one substrate is market fragmentation, not existing
practice. You are proposing the thing, not reporting it.

## The measured comparison

Same model, same task set, two harnesses: Claude Sonnet 4.5 scores 68% under
SWE-Agent and 34% under HAL Generalist (arXiv:2605.23950).

That single comparison is the whole business case. It says the platform, not
the model, sets what you get. And it is published, which means you do not need
to run a freeze-and-measure experiment nobody in the audience will actually
run.

## What leadership asks for

Two things.

```
   cost per workflow          what leadership asks for. The FinOps Foundation
                              framework still meters cost per token and cost
                              per inference; the workflow number is the one
                              you have to derive

   a maturity roadmap         where you are, what the next level demands,
                              and which path goes first
```

One supporting figure worth quoting, because it is sourced: 98% of FinOps
practitioners now manage AI spend, up 67 points from 31% two years ago (State
of FinOps 2026, n=1,192).

## Run it

```
python3 module8/run.py
```

Shows the software paths and any non-software workloads declared against the
same pillars.

## Your tasks

Finance wants ledger reconciliation run by an agent. You are the platform team.
They are the domain team. Your job is to hand them a manifest, not a project.

Open `config/workload-manifests/finance-reconciliation.yaml`.

**Task 1.** Name the domain owner. Not you.

**Task 2.** Set a TTL of 3600 seconds or less. The rule does not change because
the workload is finance.

**Task 3.** Write at least two entitlements as operations, not systems. Look at
how the software paths do it: `scm:read`, not `github`. Reconciliation might
need `ledger:read` and `ledger:post`.

Notice that one of those two is dangerous and one is not. That distinction is
the entire reason the unit of governance is the operation.

**Task 4.** Declare the data class. Financial ledger data is not internal by
default, and Module 5 taught you what happens to the routing when it is not.

**Task 5.** Grant a control mode. Reconciliation that posts to a ledger is not
assistive work, and it is not bounded autonomy on day one either.

**Task 6.** Bound the loop. Iteration cap and cost budget. Every loop needs a
way to stop, whatever the domain.

**Task 7.** Define done, and route a low score to a person. Reconciliation has
a crisp deterministic gate available to it: the ledger balances or it does not.
Say so.

**Task 8.** Set a cost per workflow target. This is the number leadership asks
for.

**Task 9.** Confirm you did not need a fourth permission tier. If a finance
workload forced one, your tier map was software-specific and the reuse claim
was never true.

Then:

```
python3 module8/check.py
python3 module8/run.py
```

## Discussion

Two questions worth the last ten minutes.

Which of the nine fields were finance-specific, and which were the
same decisions you made for `/pr-review` with different values? That ratio is
the reuse argument, measured on your own work rather than asserted.

And: who in your organization would own this manifest, and who would review it?
If the answer is that nobody knows, that is the roadmap item, not the tooling.

## Done when

Nine PASS lines, and a finance workload running on a substrate built for
software delivery, with no new pillars.
