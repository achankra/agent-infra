"""Evaluation. Whether the output ships.

Deterministic gates decide. The judge scores and routes. A judge is not
reliable enough to be a gate: across 21 judges and roughly 541,000 judgments,
rankings shifted by up to 14 positions across benchmarks and production judges
held test-retest reliability above 0.95 while carrying position bias above
0.10. A judge that agrees with itself and is still wrong is the worst case. So a low score routes to a human and never hard-fails the loop.

    artifact -> [ gates: exit codes ] -> fail -> back to the loop
                        |
                       pass
                        v
                 [ judge: score ] -> low  -> human review
                                  -> high -> promote
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from . import config

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class GateResult:
    name: str
    category: str
    passed: bool
    output: str


@dataclass
class Score:
    total: float
    band: str
    per_criterion: dict[str, float] = field(default_factory=dict)
    route: str = "review"


@dataclass
class Verdict:
    gates: list[GateResult]
    score: Score | None
    action: str          # promote | retry | review | revert
    reason: str

    @property
    def gates_passed(self) -> bool:
        return all(g.passed for g in self.gates)


class Evaluator:
    """Reads config/gates.yaml, config/eval-rubrics/ and config/promotion-rules.yaml."""

    def __init__(self, obs=None) -> None:
        self.obs = obs
        self.gates_doc = config.load_yaml("gates.yaml")
        self.rules = config.load_yaml("promotion-rules.yaml")
        self.rubrics = {}
        d = config.CONFIG / "eval-rubrics"
        if d.exists():
            for f in sorted(d.glob("*.yaml")):
                doc = config.load_yaml(f"eval-rubrics/{f.name}")
                self.rubrics[doc.get("path", f.stem)] = doc

    # -- deterministic gates ------------------------------------------
    def run_gates(self, path_name: str, workdir: Path | None = None) -> list[GateResult]:
        results = []
        for g in self.gates_doc.get("gates", []):
            if path_name not in g.get("paths", [path_name]):
                continue
            cmd = g["run"]
            proc = subprocess.run(
                cmd, shell=True, cwd=str(workdir or ROOT),
                capture_output=True, text=True, timeout=120,
            )
            passed = proc.returncode == 0
            out = (proc.stdout + proc.stderr).strip().splitlines()
            results.append(GateResult(
                name=g["name"], category=g.get("category", "functional"),
                passed=passed, output="\n".join(out[-6:]),
            ))
            if self.obs:
                self.obs.counter("gate_runs", gate=g["name"],
                                 result="pass" if passed else "fail")
        return results

    # -- the judge -----------------------------------------------------
    def judge(self, path_name: str, artifact: str) -> Score | None:
        """Scores against a rubric. Deterministic here so labs repeat, but the
        shape matches a model judge: criteria, weights, bands."""
        rubric = self.rubrics.get(path_name)
        if not rubric:
            return None
        per: dict[str, float] = {}
        for c in rubric.get("criteria", []):
            per[c["name"]] = _signal(artifact, c.get("look_for", []),
                                     c.get("penalize", []))
        weights = {c["name"]: float(c.get("weight", 1)) for c in rubric.get("criteria", [])}
        total_w = sum(weights.values()) or 1
        total = round(sum(per[k] * weights[k] for k in per) / total_w, 3)

        band, route = "unbanded", "review"
        for b in rubric.get("bands", []):
            if total >= float(b["min_score"]):
                band, route = b["name"], b.get("route", "review")
                break
        if self.obs:
            self.obs.gauge("eval_score", total, path=path_name)
            self.obs.counter("eval_bands", band=band, path=path_name)
        return Score(total=total, band=band, per_criterion=per, route=route)

    # -- promotion -----------------------------------------------------
    def decide(self, path_name: str, gates: list[GateResult], score: Score | None) -> Verdict:
        if not all(g.passed for g in gates):
            failed = [g.name for g in gates if not g.passed]
            return Verdict(gates, score, "retry",
                           f"deterministic gate failed: {', '.join(failed)}")
        if score is None:
            return Verdict(gates, score, "promote", "gates passed, no rubric defined")
        rule = (self.rules.get("routes") or {}).get(score.route, {})
        action = rule.get("action", "review")
        reason = rule.get("reason", f"score {score.total} banded {score.band}")
        if self.obs:
            self.obs.record("platform", "eval.decide", action,
                            path=path_name, score=score.total, band=score.band)
        return Verdict(gates, score, action, reason)


def _signal(artifact: str, look_for: list[str], penalize: list[str]) -> float:
    """Fraction of wanted markers present, minus penalties. Range 0 to 1."""
    text = (artifact or "").lower()
    if not look_for:
        return 0.0
    hits = sum(1 for k in look_for if k.lower() in text)
    pen = sum(1 for k in penalize if k.lower() in text)
    return max(0.0, min(1.0, (hits / len(look_for)) - 0.25 * pen))
