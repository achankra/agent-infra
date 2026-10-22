# Module 6: Evaluation

This module builds the evaluation pillar.

## Gates and the judge

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

Deterministic gates decide whether the artifact ships. The judge scores it and
routes it.

## Judge reliability

The design of this pillar rests on two studies. A 2026 evaluation across 21
judges, 9 providers and roughly 541,000 judgments found judge rankings shifting
by up to 14 positions across benchmarks, kappa deflation of 33 to 41 points,
and production judges holding test-retest reliability above 0.95 while carrying
position bias above 0.10 (arXiv:2606.19544). A judge that is consistent and
still wrong is the worst case for a gate. Separately, RAND's harness found no
judge uniformly reliable across four benchmarks (arXiv:2603.05399).

Rubrics and golden sets narrow the gap, but they do not close it. For that
reason a low score routes to a human and never hard-fails the loop. This is a
deliberate design decision.

## Codifying the definition of done

Gates are the codified definition of done. If a criterion cannot be expressed
as a command with an exit code, it belongs in the rubric instead, where it
routes the artifact rather than deciding its fate.

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

`config/agent-slos.yaml` carries six metrics, each with a healthy band and a
threshold at which to stop and investigate: confidence score, human override
rate, triage accuracy, time to resolution, false positive rate, and cost per
action. The runner prints your run against them. Nothing gates on them. They
are what you watch once the gates pass and you need to decide whether the path
is working.

## Calibration

Calibrate the judge against your own human verdicts before trusting it. The
same rubric and golden-set machinery decides which models to approve: a curated
set of 100 to 500 examples representative of your own paths, scored on your own
rubric. This is what "approved on evidence from your own paths" means in
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

**Task 2.** Write at least three weighted criteria. A good review of the seeded
defects names the defect, cites the decision record it violates, and does not
repeat credential material back into a comment.

**Task 3.** Give it three bands that route differently. High promotes, medium
takes one reviewer, low goes to a person. No band may fail the loop.

**Task 4.** Make the rubric separate a weak artifact from a strong one. Use
`penalize` as well as `look_for`. If both artifacts score the same, the rubric
is not measuring anything.

**Task 5.** Confirm the weak artifact routes to a human rather than failing.

**Task 6.** Add an architectural gate to `config/gates.yaml`. The command is
already written: `scripts/check_hot_path.py` rejects a linear scan on a hot
path, which team conventions already forbid and defect 3 in the sample app
does. Set its category to `architectural`.

**Task 7.** Make sure every gate command actually runs.

**Task 8.** Do not delete the shipped gates.

Then:

```
python3 module6/check.py
python3 module6/run.py
```

## Discussion

After Task 6, run `python3 module5/run.py` again. The loop now has a third gate
to converge on, and the agent in this repo only knows how to fix two of the
failures. Check which stop fires.

Adding a gate adds a real constraint, and the loop has to be able to satisfy
it or escalate.

## Done when

Eight PASS lines, and the weak artifact routes to a person while the strong one
promotes.
