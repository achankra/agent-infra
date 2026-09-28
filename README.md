# Agent Infrastructure: the lab repo

Ajay Chankramath, PlatformEngineering.org. MIT licensed; see LICENSE.

Companion repo for Course 3, Building Agent Infrastructure. Eight modules, one
accumulating repository. Each lab extends the last. Nothing is thrown away and
nothing is rebuilt.

Every pillar in this course is a file. You will not write Python. You will edit
declarative config and watch behavior change.

## What you build

```
                        LAYER 1  TOOLING (your IDP, already yours)
                        github   argocd   prometheus   knowledge-base
                                        ^
                                        | tool calls, through one gateway
                                        |
   +------------------------------------+-------------------------------+
   |                    LAYER 3  AGENT INFRASTRUCTURE                    |
   |                                                                     |
   |  GOVERNANCE  built once, enforced everywhere                        |
   |    identity          spiffe-ids.yaml         module 3               |
   |    agent security    permission-tiers.yaml   module 3               |
   |    observability     otel-collector.yaml     module 3               |
   |    spend ceilings    budget-policy.yaml      module 1               |
   |                                                                     |
   |  HARNESS  the machinery of one turn, configured per path            |
   |    capability        tool-registry.yaml      module 2               |
   |    context           rag-config.toml         module 4               |
   |    execution         orchestrator.yaml       module 5               |
   |    evaluation        gates.yaml, rubrics     module 6               |
   |                                                                     |
   |  MODELS  what agents consume                                        |
   |    providers         providers.yaml          module 5               |
   |    endpoints         model-routes.toml       module 5               |
   |    hosting           providers.yaml          module 5               |
   +---------------------------------------------------------------------+
                                        |
                                        v
                        LAYER 2  PATH DEFINITIONS
                        /pr-review     /validate-change
```

Modules 1, 7 and 8 do not add a pillar. Module 1 is the map, module 7 takes one
path through every pillar, module 8 points the same substrate at a workload
that has nothing to do with software.

## Where the ideas come from

`REFERENCES.md` maps each pillar back to the chapter it came from, across
*Effective Platform Engineering*, *The Platform Engineer's Handbook* and
*Domain-Driven Platform Engineering*. None of this is new. It is the platform
argument, pointed at a non-human principal.

## Setup

```
git clone https://github.com/achankra/agent-infra.git
cd agent-infra
```

Python 3.11 or newer. Nothing else is required, and no provider account is
needed for any lab.

macOS and Linux:

```
./run.sh up
```

Windows:

```
.\run.ps1 up
```

That checks your Python version, installs PyYAML if it is missing, and starts
the metrics server on http://127.0.0.1:8080/metrics.

For the dashboard, see `grafana/README.md`. The labs work without it; the
dashboard is where each one ends.

## How a lab works

```
   read the module README
            |
            v
   python3 moduleN/run.py        shows the current state of the pillar
            |
            v
   edit the config files         this is the actual work
            |
            v
   python3 moduleN/check.py      tells you which tasks are done
            |
            v
   python3 moduleN/run.py        behavior has changed
            |
            v
   refresh Grafana               a panel that read 0 now reads something
```

`check.py` prints PASS or TODO per task and names the file to open. It never
tells you the answer.

## Modules

| Module | Pillar built | Config you edit |
|---|---|---|
| 1 | none, this is the map | `module1/pillars.yaml`, read `budget-policy.yaml` |
| 2 | capability | `tool-registry.yaml`, `entitlement-map.yaml`, `mcp-gateway.tf` |
| 3 | identity, security, observability | `spiffe-ids.yaml`, `permission-tiers.yaml`, `otel-collector.yaml` |
| 4 | context | `rag-config.toml`, `data-contracts/` |
| 5 | execution, models | `orchestrator.yaml`, `sandbox.tf`, `runtime-pool.tf`, `providers.yaml`, `model-routes.toml` |
| 6 | evaluation | `gates.yaml`, `eval-rubrics/`, `promotion-rules.yaml` |
| 7 | capstone, all of them | a new path across every file |
| 8 | the substrate beyond software | `workload-manifests/` |

## Layout

```
agent-infra/
  run.sh  run.ps1        bring the stack up, check everything, reset
  substrate/             the platform, built once. You do not edit this.
    identity.py          workload identity
    policy.py            tiers, the three-check gate
    registry.py          tool registry and entitlements
    gateway.py           the tool gateway
    context.py           context assembly and compaction
    orchestrator.py      the runtime and the three stops
    models.py            the model gateway
    evaluation.py        gates, rubric, promotion
    observability.py     traces, metrics, audit
    paths/               /pr-review and /validate-change
  config/                every pillar, as declarative config. You edit this.
  sample_app/            the service the paths operate on, with seeded defects
  scripts/               gate commands, reset, lab helpers
  module1..8/            run.py, check.py and the lab README
  grafana/               dashboard and prometheus config
```

## The two paths

`/pr-review` is read-only, which is the lowest-risk way into production. It
reads a diff, searches decision records, and posts a comment. It may not merge,
because ADR 0007 says agents do not merge and `permission-tiers.yaml` enforces
that as config rather than convention.

`/validate-change` is the hybrid path. An agent proposes, a deterministic gate
verifies, and the loop repeats until the gate passes or a stop fires.

```
   /pr-review                        /validate-change

   identity                          submit
      |                                 |
   context                           [ gate ] --pass--> [ judge ] --> promote
      |                                 |                             review
   capability                          fail
      |                                 |
   model                             agent reads the structured failure,
      |                              fixes, resubmits
   evaluation                          |
                                    stops on: iteration cap
                                              stall detection
                                              cost budget
```

## Simulate and live

Every lab runs in simulate mode by default, with no API key. Model calls are
deterministic so a lab repeats identically.

To run against a real model, name the provider's key variable in
`config/providers.yaml`, export it, and pass `--live`:

```
export FRONTIER_VENDOR_API_KEY=...   # never paste a key into a shared screen
python3 module5/run.py --live
```

Which vendor that is, which wire format it speaks and which environment
variable holds its credential are all config. Nothing in `substrate/` names a
vendor, which is the same rule every other pillar follows.

The governance layer is identical in both modes. That is the point of the
split: the safety properties come from the platform, not from the model.

## Reset

```
./run.sh reset
```

Restores `sample_app/` to its seeded state and clears `.state/`. Run it between
cohorts. Your `config/` edits are not touched, because those are your work.

## Check everything

```
./run.sh check
```

Runs all eight checkers. Exit code 0 means every task in the course is done.
