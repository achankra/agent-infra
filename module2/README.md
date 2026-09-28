# Module 2: the tooling layer, and what agents reach into

45 minutes. Builds the capability pillar.

## Your IDP is already the tooling layer

The systems in this repo are the ones you already run: source control, CI,
telemetry, a knowledge base. CI/CD, resources, scanners and dashboards carry
over unchanged. Deterministic paths run start to finish on this layer with no
agent anywhere.

What is new is the governed interface an agent reaches it with.

## The tool is the system. The capability is the grant.

```
   LAYER 1 TOOLING                    CAPABILITY PILLAR

   the systems themselves,            the governed exposure of those
   which existed before agents        systems to an agent
   and serve humans too

   unit: a system    (github)         unit: an operation (scm:read,
                                            ci:trigger, scm:merge)

   owned by: platform, already        owned by: platform, newly

   answers: what exists               answers: what may this agent call,
                                               described so a machine can
                                               consume it
```

One Layer 1 system yields many capabilities, each separately entitled and
separately tiered. GitHub is one system and at least four grants.

Capability is broader than "Layer 1 with an API". Skills and procedures, MCP
servers wrapping internal APIs, and agent-to-agent calls are all capability
grants, and none of them is a Layer 1 system.

## The gateway is the doorway

```
   without a gateway                  with a gateway

   agent ---> github                  agent ---\
   agent ---> argocd                  agent -----> [ tool gateway ] ---> github
   agent ---> prometheus              agent ---/     authorization        argocd
                                                     rate limits          prometheus
   N integrations,                                   audit
   N authorization points
                                                   one place, N systems
```

These are self-hosted MCP servers, one per system, behind a gateway you run
in-cluster. `mcp-gateway.tf` is our gateway in front of our own servers, not a
vendor subscription.

There is a second gateway later in the course. This one governs what an agent
can **do**. The model gateway in Module 5 governs what it can **think with**.
Same pattern, different subject.

I made this argument before agents existed. *Effective Platform Engineering*,
Ch 4: infrastructure available through the platform is provisioned by the
platform on the team's behalf rather than merely granting the team permissions
to do it themselves. Replace "team" with "agent" and that is this module.

## Fewer tools beat more

This is measured, not a preference. Llama 3.1 8B fails a function-calling
benchmark at 46 tools and passes the same set at 19 (arXiv:2411.15399). That
is a small model, so read it as the shape rather than the threshold: for
frontier models the overlap onset is nearer 30, and vendors have converged on
caps of 40 to 50.

Two causes. Every tool definition sits in the context window at 300 to 600
tokens each, spent before any work happens. GitHub's MCP server alone is about
26,000 tokens for 35 tools. And more options mean more chances
to pick the wrong one.

So handing an agent everything available makes it worse, not more capable.
Curation is a platform decision. Left to the path author, the answer is always
"all of them".

## Run it

```
python3 module2/run.py
```

You will see the systems, the operations each one yields, what `/pr-review` is
entitled to, and what those tool definitions cost in tokens before any work
happens.

## Your tasks

An on-call engineer wants `/pr-review` to check whether the service under
review is currently erroring before it comments. That means one new capability:
`telemetry:query`, backed by Prometheus, which you already run.

Adding it takes five edits in five files. That is the lesson.

```
   1. tool-registry.yaml     does the operation exist at all
   2. entitlement-map.yaml   may this path call it
   3. mcp-gateway.tf         is the backing server reachable
   4. permission-tiers.yaml  how dangerous is it
   5. spiffe-ids.yaml        does the identity carry the entitlement
```

**Task 1.** Add `telemetry:query` to `config/tool-registry.yaml`. System is
`prometheus`, kind is `mcp`, and give it a `token_cost`. Write a description a
machine can act on.

**Task 2.** Grant it to `/pr-review` in `config/entitlement-map.yaml`.

**Task 3.** Enable the `prometheus` server in `enabled_servers` in
`config/mcp-gateway.tf`. Until you do, the registry knows the operation and the
gateway still refuses it. Two doors, both must be open.

**Task 4.** Give it a tier in `config/permission-tiers.yaml`. Reading telemetry
is not the same risk as merging. Anything unlisted classifies dangerous by
omission, so leaving it out is a decision too.

**Task 5.** Add it to the pre-provisioned identity in `config/spiffe-ids.yaml`.
That identity ships with the repo so you can scope an entitlement before Module
3 teaches how to issue one.

Then:

```
python3 module2/check.py
python3 module2/run.py
```

## Discussion

After the check passes, look at the token cost line in `run.py` output. You
added the `token_cost` you chose to the context every run now pays, whether or
not the tool is used. Read the before and after totals, not the delta: the
entitled set moves from roughly 740 tokens to over a thousand for one
read-only tool. Curation has a price on both sides.

## Done when

Five PASS lines, and the last one is an agent actually completing the call end
to end.
