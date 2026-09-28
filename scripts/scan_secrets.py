"""The policy gate. Scans source for credential material. Exit code is the verdict."""
from __future__ import annotations

import re
import sys
from pathlib import Path

PATTERNS = {
    "bearer_token": re.compile(r"(?i)bearer\s+[a-z0-9._-]{24,}"),
    "aws_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "private_key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
}


def main(argv: list[str]) -> int:
    target = Path(argv[1] if len(argv) > 1 else "sample_app/src")
    findings = []
    files = [target] if target.is_file() else sorted(target.rglob("*.py"))
    for f in files:
        text = f.read_text()
        for lineno, line in enumerate(text.splitlines(), 1):
            for name, pat in PATTERNS.items():
                if pat.search(line):
                    findings.append(f"{f}:{lineno} {name}")
    for hit in findings:
        print(f"FINDING {hit}")
    print(f"scanned {len(files)} file(s), {len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
