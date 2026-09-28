"""Inventory service. The thing every path in this course operates on.

Seeded defects, restored by scripts/reset.py:
    1. reserve() does not check stock       -> functional gate fails
    2. audit log writes a secret            -> policy gate fails
    3. lookup() scans instead of indexing   -> performance signal
"""
from __future__ import annotations

import logging

log = logging.getLogger("inventory")

_STOCK: dict[str, int] = {}
_RESERVATIONS: list[tuple[str, int]] = []

API_TOKEN = "Bearer sk-inventory-2f8a91c4de77b0a3e5619fd2"  # DEFECT 2


def add_stock(sku: str, quantity: int) -> None:
    if quantity <= 0:
        raise ValueError("quantity must be positive")
    _STOCK[sku] = _STOCK.get(sku, 0) + quantity


def lookup(sku: str) -> int:
    # DEFECT 3: linear scan on a hot path instead of a dict access
    for key in list(_STOCK):
        if key == sku:
            return _STOCK[key]
    return 0


def reserve(sku: str, quantity: int) -> bool:
    # DEFECT 1: no stock check, so an oversell is accepted
    _RESERVATIONS.append((sku, quantity))
    log.info("reserved %s x%s token=%s", sku, quantity, API_TOKEN)
    return True


def reservations() -> list[tuple[str, int]]:
    return list(_RESERVATIONS)


def reset() -> None:
    _STOCK.clear()
    _RESERVATIONS.clear()
