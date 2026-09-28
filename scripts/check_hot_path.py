"""An architectural gate. Rejects a linear scan over a dict on a hot path.

Team conventions say hot paths index into structures. This encodes that as a
command with an exit code, so it decides rather than advises.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

HOT = {"lookup", "get", "fetch"}


def main(argv: list[str]) -> int:
    target = Path(argv[1] if len(argv) > 1 else "sample_app/src")
    files = [target] if target.is_file() else sorted(target.rglob("*.py"))
    findings = []
    for f in files:
        try:
            tree = ast.parse(f.read_text())
        except SyntaxError as e:
            print(f"FINDING {f}: does not parse: {e}")
            return 1
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in HOT:
                for sub in ast.walk(node):
                    if isinstance(sub, ast.For):
                        findings.append(
                            f"{f}:{sub.lineno} linear scan inside hot path "
                            f"{node.name}()")
    for hit in findings:
        print(f"FINDING {hit}")
    print(f"scanned {len(files)} file(s), {len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
