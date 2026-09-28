"""Checks Module 1 tasks."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import yaml  # noqa: E402
from scripts.lab import Checker  # noqa: E402

HERE = Path(__file__).resolve().parent

EXPECTED_OWNER = {
    "identity": "governance", "agent-security": "governance",
    "agent-observability": "governance", "capability": "harness",
    "context": "harness", "execution": "harness", "evaluation": "harness",
    "providers": "models", "inference-endpoints": "models",
    "model-hosting": "models",
}

EXPECTED_AUTHORITY = {
    "identity scope": "platform",
    "which entitled tools this path uses": "path-owner",
    "policy tier map": "platform",
    "iteration ceiling": "path-owner",
    "cost cap": "platform",
    "definition of done": "path-owner",
}


def main() -> int:
    c = Checker("Module 1: the substrate that runs paths")
    doc = yaml.safe_load((HERE / "pillars.yaml").read_text())

    pillars = {p["name"]: p for p in doc.get("pillars", [])}
    filled = [n for n, p in pillars.items() if str(p.get("owner")).lower() != "todo"]
    c.task(1, "every pillar has an owner", len(filled) == 10,
           f"{10 - len(filled)} still say TODO in module1/pillars.yaml")

    wrong = [n for n, p in pillars.items()
             if str(p.get("owner", "")).lower() not in ("todo",)
             and str(p.get("owner", "")).lower() != EXPECTED_OWNER.get(n)]
    c.task(2, "each pillar sits in the right block", len(filled) == 10 and not wrong,
           f"check these: {', '.join(wrong)}" if wrong else
           "finish Task 1 first")

    params = {p["name"]: str(p.get("authority", "")).lower()
              for p in doc.get("parameters", [])}
    unfilled = [k for k, v in params.items() if v == "todo"]
    bad = [k for k, v in params.items()
           if v != "todo" and v != EXPECTED_AUTHORITY.get(k)]
    c.task(3, "authority assigned for all six parameters",
           not unfilled and not bad,
           (f"still TODO: {', '.join(unfilled)}" if unfilled else
            f"reconsider: {', '.join(bad)}. A path owner chooses inside the "
            f"envelope; the platform grants the envelope."))
    return c.report()


if __name__ == "__main__":
    raise SystemExit(main())
