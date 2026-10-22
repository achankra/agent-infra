# Module 5: Execution and Models

This module builds the execution pillar and the three pillars that make up
models.

Course 2 covered the ReAct loop and the hybrid path. This module covers where
that loop runs and what bounds it.

## Ephemeral workspaces

```
   dispatch
      |
      v
   [ ephemeral workspace ]   checkout, loop, builds, tests
      |                      isolated: parallel runs cannot see each other
      |                      no network unless allowlisted
      v                      destroyed at exit, no state leaks, no idle cost
   destroyed
```

Common implementations include an ephemeral cloud sandbox VM per task, one Git
worktree per agent, and hardened unprivileged containers per run. CI runners
were the original ephemeral workspace, so your existing pipeline
infrastructure is already most of an agent execution substrate.

Orchestration walks the graph, sequences steps, holds state and retries.
Because state is checkpointed, a crashed run resumes instead of restarting.

## Bounding the loop

```
   iteration cap      the loop has run enough times
   stall detection    no measurable progress across a window of iterations
   cost budget        tokens or dollars spent
```

A stall usually points to an ambiguous goal or missing context. Raising the
budget will not fix it, so detect the stall and stop.

The lab measures what bounding saves. An unconverging run stops at the
runner's hard limit having spent $0.0150, and the same work bounded converges
for $0.0004. Anthropic reports single agents using about 4x the tokens of a
chat interaction and multi-agent systems about 15x, so the cost multiplies
further as soon as you add a second agent.

You cannot raise the cost budget on your own. `config/budget-policy.yaml` is
governance, granted centrally in Module 1, and a run that asks for more than
the ceiling gets the ceiling, with the decision recorded. You can set a lower
budget than the platform allows, but not a higher one.

## Control modes

A control mode sets how much autonomy a path is granted, from assistive to
bounded autonomy. Autonomy is granted to each path separately. This module
builds the runtime that holds an agent inside the mode its path was granted.

## The model gateway

```
   agent ---\                          the tool gateway from Module 2 governs
   agent -----> [ model gateway ] -->  what an agent can DO
   agent ---/     routing by task,
                  cost and data class  this one governs what it can THINK WITH
                  brokered keys
                  quotas               clients authenticate to the gateway,
                  metering             never to the provider
```

The case for brokered keys comes from an incident. In May 2026 an eval vendor
suffered a breach that exposed customer API keys. Treat any key held by a
third party you did not threat-model as already compromised.

Model access involves three decisions, and only one of them is a component you
build.

```
   PROVIDERS      which models are approved, on what terms,
                  pinned to which versions               a policy you encode

   ENDPOINTS      one gateway, managed APIs, routing,
                  brokered keys, quotas, metering        a component you build

   HOSTING        private tenancy or self-hosted,
                  decided by data class, latency, cost   a policy you encode
```

Pin every model version. Providers update and deprecate models without notice,
and unpinned versions make gate results incomparable across runs. This repo
refuses to load a model spec without a pinned version.

Approval should rest on evidence from your own paths. A public leaderboard
does not measure your paths. Module 6 builds the rubric and
golden sets that produce that evidence.

## Run it

The repo ships with all three bounds unset.

```
python3 module5/run.py --no-fix
```

With `--no-fix`, the agent proposes nothing, so the loop cannot converge. Watch
the iteration count and the spend. The loop stops only because the runner has
a hard limit, which exists to keep the lab from hanging.

## Your tasks

**Task 1.** Set `bounds.iteration_cap` in `config/orchestrator.yaml`.

**Task 2.** Set `bounds.stall_window`, and choose the value deliberately. If it
is too small, a slow-converging loop is killed. If it is too large, you pay for
iterations that make no progress.

**Task 3.** Set `bounds.cost_budget_usd`.

**Task 4.** Rerun with `--no-fix` and confirm the loop now stops on one of
your bounds. The stop reason should name which bound fired.

**Task 5.** Swap the model behind a route. `/pr-review` is read-only work and
does not need the expensive model. Route it to `small` in
`config/model-routes.toml`. It is a one-line change, and no code changes.

**Task 6.** Finance wants `/validate-change` run against confidential ledger
data. Try it, read the error, then fix the routing so confidential work lands
on a model approved to hold it. Note which of the three models qualifies and
why. This is the hosting decision, and it is made by data class.

**Task 7.** Confirm no unapproved provider is reachable from any route.

Then:

```
python3 module5/check.py
python3 module5/run.py --no-fix
python3 module5/run.py
```

## Discussion

Compare the cost of the last two runs. Then estimate what a loop that never
converges would cost without the three bounds, running in production
overnight.

## Done when

Seven PASS lines, and `--no-fix` stops on one of your three bounds rather than
on the runner's hard limit.
