"""The functional gate. Exit code is the verdict."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import inventory  # noqa: E402


def test_add_and_lookup() -> None:
    inventory.reset()
    inventory.add_stock("SKU-1", 10)
    assert inventory.lookup("SKU-1") == 10


def test_reserve_rejects_oversell() -> None:
    inventory.reset()
    inventory.add_stock("SKU-1", 3)
    ok = inventory.reserve("SKU-1", 5)
    assert ok is False, "reserve accepted an oversell: 5 requested, 3 in stock"


def test_reserve_accepts_valid() -> None:
    inventory.reset()
    inventory.add_stock("SKU-1", 5)
    assert inventory.reserve("SKU-1", 2) is True


def main() -> int:
    failures = []
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as e:
                print(f"FAIL {name}: {e}")
                failures.append(name)
    print(f"\n{len(failures)} failed, "
          f"{sum(1 for n in globals() if n.startswith('test_')) - len(failures)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
