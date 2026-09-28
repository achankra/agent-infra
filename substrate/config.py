"""Loads the declarative artifacts in config/.

Agent Infrastructure as Code means every pillar is a version-controlled file.
This module is the only place that reads them, so a lab can change behavior by
editing a file rather than editing Python.

Formats:
    .yaml   PyYAML
    .toml   tomllib (Python 3.11+)
    .tf     a deliberately small HCL reader, see read_tf_locals
    .hcl    same reader
"""
from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config"


class ConfigError(Exception):
    """Raised when an artifact is missing or malformed. Fail loudly, not silently."""


def path(name: str) -> Path:
    p = CONFIG / name
    if not p.exists():
        raise ConfigError(f"missing artifact: config/{name}")
    return p


def load_yaml(name: str) -> Any:
    try:
        return yaml.safe_load(path(name).read_text()) or {}
    except yaml.YAMLError as e:
        raise ConfigError(f"config/{name} is not valid YAML: {e}") from e


def load_toml(name: str) -> dict:
    try:
        return tomllib.loads(path(name).read_text())
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"config/{name} is not valid TOML: {e}") from e


_BLOCK = re.compile(r"^\s*locals\s*\{", re.M)


def read_tf_locals(name: str) -> dict[str, Any]:
    """Read the top-level locals block from a .tf or .hcl file.

    This is not a general HCL parser. It handles the shapes used in this repo:
    strings, numbers, booleans, and flat lists of strings. Anything else is
    ignored rather than guessed at.
    """
    text = path(name).read_text()
    m = _BLOCK.search(text)
    if not m:
        raise ConfigError(f"config/{name} has no locals block")

    depth, i = 0, m.end() - 1
    for j in range(m.end() - 1, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                i = j
                break
    body = text[m.end() : i]

    out: dict[str, Any] = {}
    for line in _strip_comments(body).splitlines():
        line = line.strip().rstrip(",")
        if not line or "=" not in line:
            continue
        key, _, raw = line.partition("=")
        key, raw = key.strip(), raw.strip()
        if not key.isidentifier():
            continue
        out[key] = _coerce(raw)

    for key, raw in _list_assignments(_strip_comments(body)):
        out[key] = raw
    return out


def _strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"(#|//).*$", "", text, flags=re.M)


def _list_assignments(body: str) -> list[tuple[str, list[str]]]:
    out = []
    for m in re.finditer(r"(\w+)\s*=\s*\[(.*?)\]", body, re.S):
        items = [x.strip().strip('"').strip("'") for x in m.group(2).split(",")]
        out.append((m.group(1), [x for x in items if x]))
    return out


def _coerce(raw: str) -> Any:
    if raw.startswith("["):
        return []
    if raw in ("true", "false"):
        return raw == "true"
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    if re.fullmatch(r"-?\d*\.\d+", raw):
        return float(raw)
    return raw.strip('"').strip("'")


def exists(name: str) -> bool:
    return (CONFIG / name).exists()
