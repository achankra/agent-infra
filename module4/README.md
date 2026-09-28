# Module 4: Context

This module runs for 45 minutes and builds the context pillar.

## Explicit and implicit

Context is what you hand the agent, and what it assumes because you did not.
Every gap is filled by a guess.

Context splits into two categories, each with its own retrieval method.

```
   KNOWLEDGE                          LIVE SYSTEMS
   code, tickets, runbooks,           telemetry, CI/CD, SaaS tools
   incident history, service
   catalog, CI/CD history

   retrieved by RAG                   retrieved by MCP
```

Memory is separate again, and it comes in tiers: episodic, semantic,
procedural. Procedural memory is learned tool-use and workflow patterns, and it
is the one most curricula leave out.

## The context window, memory, and compaction

The context window exists per turn.

```
   accuracy
     ^
     |  ####                      ####     a fact at the start or the end is
     |      ##                  ##         recalled. The same fact in the
     |        ####          ####           middle is not.
     |            ##########
     +-------------------------------> position in the window

   Accuracy falls more than 20 points when the key fact sits mid-context, on
   a U-shaped curve against position. At worst it drops below the closed-book
   baseline, which is the sharper way to say it: the document made things
   worse than no document at all (Liu et al., arXiv:2307.03172).
```

Context rot is quality falling as the window fills, and with where a fact sits
in it. The useful framing is a maximum effective context window: effective
limits are task-dependent, so compaction thresholds are set per task rather
than once globally.

Compaction runs before the window degrades, not after. A summary written after
rot has set in is itself degraded, because the model producing it is already
impaired. The trigger point is the design decision.

## Certified sources and data contracts

Every source is certified, carries a contract, and has an owner. A data contract carries schema, quality rules,
semantic definitions, an SLA and an owner, and it is a gating prerequisite for
agentic work.

In this repo a source without a contract is not assembled. It is reported.

```
   source named in rag-config.toml
        |
        v
   does it have a data contract?  --no--> dropped, and reported
        |
       yes
        |
        v
   is the contract certified?  --no--> dropped, and reported
        |
       yes
        |
        v
   assembled, and counted against the window
```

## Run it

```
python3 module4/run.py
```

You will see what assembles today, what is dropped and why, and the same path
against a dump-everything baseline.

## Your tasks

`/pr-review` currently sees the diff and nothing else. It is reviewing a change
against conventions it has never been shown, and a ticket it has never read.

**Task 1.** Add `adrs` to the sources for `/pr-review` in
`config/rag-config.toml`. It is knowledge, retrieved by RAG.

**Task 2.** Add `ticket`. It is a live system, retrieved by MCP.

**Task 3.** The ticket has no data contract, so it will be dropped. Create
`config/data-contracts/ticket.yaml` with source, owner, certified, schema,
semantics, quality_rules and sla. Copy the shape from `diff.yaml`, and put a
real owner in it.

**Task 4.** Certify it, once you have named an owner and an SLA.

**Task 5.** Confirm all three sources actually assemble.

**Task 6.** Check the token count against the window. If you are over the
compaction trigger, decide deliberately: lower the trigger, or drop a source.
Both answers are legitimate. Guessing between them is not.

**Task 7.** Compare against the dump-everything number in the runner output.

Then:

```
python3 module4/check.py
python3 module4/run.py
```

## Discussion

The ticket you just assembled contains an instruction pasted from a customer
email. If you did Module 3 Task 5, the input check catches it. If you did not,
`run.py` will tell you it is being allowed.

That is the whole argument for treating a live source as untrusted input. A
ticket is data. Assembled into context without screening, its contents become
instructions.

## Done when

Seven PASS lines, and the runner shows three certified sources assembling with
the ticket screened.
