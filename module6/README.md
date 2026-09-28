# Module 6: evaluation, whether the output ships

45 minutes. Builds the evaluation pillar.

## Two mechanisms, one decision

```
   artifact
      |
      v
   [ DETERMINISTIC GATES ]   exit codes. no model anywhere.
      |                      lint, tests, policy scan, architecture check
      |
   fail -> back to the loop with a structured failure
      |
     pass
      |
      v
   [ THE JUDGE ]             scores against a rubric
      |
   low  -> a person decides
   high -> promote
```

Deterministic gates decide. The judge scores and routes.

## The judge cannot be the gate

This is the load-bearing claim of the module, and it rests on two studies
rather than one. A 2026 evaluation across 21 judges, 9 providers and roughly
541,000 judgments found judge rankings shifting by up to 14 positions across
benchmarks, kappa deflation of 33 to 41 points, and production judges holding
test-retest reliability above 0.95 while carrying position bias above 0.10
(arXiv:2606.19544). A judge that agrees with itself and is still wrong is the
worst case for a gate. Separately, RAND's harness found no judge uniformly
reliable across four benchmarks (arXiv:2603.05399).

Rubrics and golden sets narrow the gap. They do not close it.

So a low score routes to a human. It never hard-fails the loop. That is a
design decision, not a limitation you work around later.

## The definition of done, written down

Gates are the codified definition of done. If a criterion cannot be expressed
as a command with an exit code, it belongs in the rubric instead, and it routes
rather than decides.

```
   category         example                              decides?
   functional       tests pass                           yes
   policy           no credential material in source     yes
   architectural    hot paths index, they do not scan    yes
   operational      the run stayed inside its budget     yes
   subjective       the summary cites the decision       no, it scores
                    record it claims to follow
```

## Operating metrics

The judge is not the only thing worth measuring. `config/agent-slos.yaml`
carries six metrics with a healthy band and the point at which to stop and
look: confidence score, human override rate, triage accuracy, time to
resolution, false positive rate, and cost per action. The runner prints your
run against them. Nothing gates on them, deliberately. They are what you watch
in week two, once the gates pass and you have to decide whether the path is
working.

## Calibration

Calibrate the judge against your own human verdicts before trusting it. The
same rubric and golden-set machinery answers which models to approve: a curated
set of 100 to 500 examples representative of your own paths, scored on your own
rubric. That is what "approved on evidence from your own paths" means back in
Module 5.

## Run it

```
python3 module6/run.py
```

You will see the gates, the rubric, and two artifacts scored against it, one
well-formed and one weak.

## Your tasks

`/validate-change` has a rubric. `/pr-review` does not, so its output ships on
gates alone with nothing checking whether the review is any good.

**Task 1.** Create `config/eval-rubrics/pr-review.yaml`. Set `path: /pr-review`.

**Task 2.** Write at least three weighted criteria. A rubric with one criterion
is a preference. Look at what a good review of the seeded defects would
actually say: it names the defect, cites the decision record it violates, and
does not repeat credential material back into a comment.

**Task 3.** Give it three bands that route differently. High promotes, medium
takes one reviewer, low goes to a person. No band may fail the loop.

**Task 4.** Make the rubric separate a weak artifact from a strong one. Use
`penalize` as well as `look_for`. If both score the same, the rubric is
decoration.

**Task 5.** Confirm the weak artifact routes to a human rather than failing.

**Task 6.** Add an architectural gate to `config/gates.yaml`. One is written
for you: `scripts/check_hot_path.py` rejects a linear scan on a hot path, which
is what team conventions already say and what defect 3 in the sample app does.
Set its category to `architectural`.

**Task 7.** Every gate command must actually run. A gate that cannot run is not
a gate.

**Task 8.** Do not delete the shipped gates.

Then:

```
python3 module6/check.py
python3 module6/run.py
```

## Discussion

After Task 6, run `python3 module5/run.py` again. You added a gate, so the loop
now has a third thing to converge on, and the agent in this repo only knows how
to fix two of them. Watch which stop fires.

That is what adding a gate costs: it is a real constraint, and the
loop has to be able to satisfy it or escalate.

## Done when

Eight PASS lines, and the weak artifact routes to a person while the strong one
promotes.
