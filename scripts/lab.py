"""Shared helpers for module runners and checkers.

check.py in each module prints one line per task. Green means the participant
changed the config; red says which file to open and what is missing.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

GREEN, RED, DIM, BOLD, RESET = "\033[32m", "\033[31m", "\033[2m", "\033[1m", "\033[0m"


class Checker:
    def __init__(self, module: str) -> None:
        self.module = module
        self.results: list[tuple[str, bool, str]] = []

    def task(self, n: int, name: str, ok: bool, hint: str = "") -> None:
        self.results.append((f"Task {n}: {name}", bool(ok), hint))

    def report(self) -> int:
        print(f"\n{BOLD}  {self.module}{RESET}")
        print("  " + "-" * 62)
        for name, ok, hint in self.results:
            mark = f"{GREEN}PASS{RESET}" if ok else f"{RED}TODO{RESET}"
            print(f"  {mark}  {name}")
            if not ok and hint:
                print(f"        {DIM}{hint}{RESET}")
        done = sum(1 for _, ok, _ in self.results if ok)
        print("  " + "-" * 62)
        print(f"  {done}/{len(self.results)} complete\n")
        return 0 if done == len(self.results) else 1


def header(title: str, subtitle: str = "") -> None:
    print(f"\n{BOLD}  {title}{RESET}")
    if subtitle:
        print(f"  {DIM}{subtitle}{RESET}")
    print("  " + "=" * 62)


def section(title: str) -> None:
    print(f"\n  {BOLD}{title}{RESET}")


def kv(k: str, v) -> None:
    print(f"    {k:<26} {v}")


def bullet(text: str) -> None:
    print(f"      {text}")


def dashboard_note() -> None:
    print(f"\n  {DIM}Metrics written to .state/metrics.prom. "
          f"If the stack is up, refresh Grafana.{RESET}\n")
