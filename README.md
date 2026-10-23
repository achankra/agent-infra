# Agent Infrastructure: the lab repo

Ajay Chankramath, PlatformEngineering.org. MIT licensed; see LICENSE.

Companion repo for Course 3, Building Agent Infrastructure. All eight modules
work in this one repository, and each lab builds on the one before it.

Every pillar in the course is a config file. No lab asks you to write Python.
You edit declarative config and watch the behavior change.

## Core textbook

*Thinking in Platforms* by Kaspar von Grünberg and Luca Galante (Weave
Intelligence, 2026) is the core textbook for this course. The unit every lab
operates on, the path, comes from it:

> "A path is a bounded intervention from user intent to usable output."
>
> von Grünberg and Galante, *Thinking in Platforms*, p. 94

The book also sets out what an enterprise adds to a path: identity, policy and
state. This repo builds those once, as the substrate every path runs on, and
each path declares the rest.

## What you build

```
                        LAYER 1  TOOLING (your IDP, already yours)
                        github   github-actions   argocd   prometheus   knowledge-base
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

Modules 1, 7 and 8 do not add a pillar. Module 1 lays out the map. Module 7
takes one path through every pillar. Module 8 points the same substrate at a
workload that has nothing to do with software.

## References

`REFERENCES.md` maps each pillar to the source it came from.

## Setup

```
git clone https://github.com/achankra/agent-infra.git
cd agent-infra
```

Python 3.11 or newer. Nothing else is required, and no provider account is
needed for any lab.

macOS and Linux:

```
./run.sh setup
```

Windows:

```
.\run.ps1 setup
```

That checks your Python version and installs PyYAML if it is missing.

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
```

`check.py` prints PASS or TODO per task and names the file to open. It does not
print the answer.

## Modules

| Module | Title | Pillar built | Config you edit |
|---|---|---|---|
| 1 | The substrate that runs paths | none, this is the map | `module1/pillars.yaml`; read `budget-policy.yaml` |
| 2 | The tooling layer | capability | `tool-registry.yaml`, `entitlement-map.yaml`, `mcp-gateway.tf`, `permission-tiers.yaml`, `spiffe-ids.yaml` |
| 3 | Governance | identity, security, observability | `spiffe-ids.yaml`, `permission-tiers.yaml`, `otel-collector.yaml` |
| 4 | Context | context | `rag-config.toml`, `data-contracts/` |
| 5 | Execution and Models | execution, models | `orchestrator.yaml`, `model-routes.toml`; read `sandbox.tf`, `runtime-pool.tf`, `providers.yaml` |
| 6 | Evaluation | evaluation | `eval-rubrics/pr-review.yaml`, `gates.yaml`; read `promotion-rules.yaml`, `agent-slos.yaml` |
| 7 | The Full-Path Build | capstone, all of them | `/oncall-triage` across six files: `spiffe-ids.yaml`, `entitlement-map.yaml`, `rag-config.toml`, `model-routes.toml`, `orchestrator.yaml`, `eval-rubrics/` |
| 8 | The Future of Platform Engineering | the substrate beyond software | `workload-manifests/` |

## Layout

```
agent-infra/
  run.sh  run.ps1        setup, check everything, reset
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
  scripts/
    lab.py               output helpers shared by every run.py and check.py
    reset.py             what ./run.sh reset calls
    seed/                the seeded copy of sample_app that reset restores
    scan_secrets.py      gate command run by config/gates.yaml
    check_hot_path.py    gate command run by config/gates.yaml
  module1..8/            run.py, check.py and the lab README
  answer-key/            README.md is the answer key; solved/ holds a solved
                         config/ and pillars.yaml
```

## The two paths

`/pr-review` is read-only, which is the lowest-risk way into production. It
reads a diff, searches decision records, and posts a comment. It may not merge,
because ADR 0007 says agents do not merge and `permission-tiers.yaml` enforces
that rule in config.

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
vendor.

The governance layer is identical in both modes, because the safety properties
come from the platform and do not depend on the model.

## Reset

```
./run.sh reset
```

Restores `sample_app/` to its seeded state and clears `.state/`, where runs
write `metrics.prom`, `audit.json` and `traces.json`. Run it whenever you want
a clean start. It does not touch your edits in `config/`.

## Check everything

```
./run.sh check
```

Runs all eight checkers. Exit code 0 means every task in the course is done.
