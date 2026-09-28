# Module 5: Execution and Models

This module runs for 45 minutes and builds the execution pillar along with
the three pillars that make up models.

Course 2 covered the ReAct loop and the hybrid path. This is where it runs, and
what bounds it.

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

Named implementations: an ephemeral cloud sandbox VM per task, one Git worktree
per agent, hardened unprivileged containers per run. Your CI runners were the
original ephemeral workspace, which is why your existing pipeline
infrastructure is most of an agent execution substrate already.

Orchestration walks the graph, sequences steps, holds state and retries.
Checkpointed state means a crash resumes instead of restarting.

## Bounding the loop

```
   iteration cap      the loop has run enough times
   stall detection    no measurable progress across a window of iterations
   cost budget        tokens or dollars spent
```

Stalling usually means an ambiguous goal or missing context, not a budget set
too low. Detect it rather than raising the ceiling.

Bounding pays for itself, and the lab measures it rather than quoting anyone:
an unconverging run stops at the runner's hard limit having spent $0.0150, and
the same work bounded converges for $0.0004. Anthropic reports single agents
using about 4x the tokens of a chat interaction and multi-agent systems about
15x, so the multiplier compounds the moment you add a second agent.

The cost budget is the one bound you cannot raise on your own.
`config/budget-policy.yaml` is governance, granted centrally in Module 1, and
a run asking for more than the ceiling gets the ceiling with the decision
recorded. Be more conservative than the platform whenever you like. Never
less.

## Control modes

How much autonomy a path is granted, from assistive to bounded autonomy.
Autonomy is granted per path, not per organization. This module builds the
runtime that holds an agent inside whichever mode a path was granted.

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

Brokered keys, argued from an incident: an eval vendor suffered a breach in May
2026 that exposed customer API keys. Keys held by a third party you did not
threat-model are already lost.

Three decisions, and only one of them is a component you build.

```
   PROVIDERS      which models are approved, on what terms,
                  pinned to which versions               a policy you encode

   ENDPOINTS      one gateway, managed APIs, routing,
                  brokered keys, quotas, metering        a component you build

   HOSTING        private tenancy or self-hosted,
                  decided by data class, latency, cost   a policy you encode
```

Pin the version. Models are silently updated and deprecated, and
unpinned versions make gate results incomparable across runs. This repo refuses
to load a model spec without a pinned version.

Approved on what terms means approved on evidence from your own paths, not on a
public leaderboard. Module 6 builds the rubric and golden sets that produce
that evidence.

## Run it

The repo ships with all three stops unset.

```
python3 module5/run.py --no-fix
```

`--no-fix` means the agent proposes nothing, so the loop cannot converge. Watch
the iteration count and the spend. It stops only because the runner has a hard
limit, which is not a design.

## Your tasks

**Task 1.** Set `bounds.iteration_cap` in `config/orchestrator.yaml`.

**Task 2.** Set `bounds.stall_window`. Pick a number and be ready to defend it.
Too small and a slow-converging loop is killed; too large and you pay for
nothing.

**Task 3.** Set `bounds.cost_budget_usd`.

**Task 4.** Rerun with `--no-fix` and confirm the loop now stops by design
rather than by accident. The stop reason should name which bound fired.

**Task 5.** Swap the model behind a route. `/pr-review` is read-only work and
does not need the expensive model. Route it to `small` in
`config/model-routes.toml`. One line, and no code moves.

**Task 6.** Finance wants `/validate-change` run against confidential ledger
data. Try it, read the error, then fix the routing so confidential work lands
on a model approved to hold it. Note which of the three models qualifies and
why: this is the hosting decision, made by data class rather than by
preference.

**Task 7.** Confirm no unapproved provider is reachable from any route.

Then:

```
python3 module5/check.py
python3 module5/run.py --no-fix
python3 module5/run.py
```

## Discussion

Run 4 and run 5 back to back and compare cost. Then ask what the number would
have been without the three stops, on a loop that never converges, in
production, overnight.

## Done when

Seven PASS lines, and `--no-fix` stops on one of your three bounds rather than
on the runner's hard limit.
