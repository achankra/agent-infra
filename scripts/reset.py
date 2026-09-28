"""Put the sample app back to its seeded state. Run between labs or cohorts."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "scripts" / "seed"


def main() -> int:
    if not SEED.exists():
        print("no seed snapshot found; nothing to restore")
        return 1
    target = ROOT / "sample_app"
    shutil.rmtree(target, ignore_errors=True)
    shutil.copytree(SEED / "sample_app", target)
    state = ROOT / ".state"
    shutil.rmtree(state, ignore_errors=True)
    print("sample_app restored to seeded state, .state cleared")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
