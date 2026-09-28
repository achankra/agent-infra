# ADR 0011: Stock invariants are enforced at reservation time

Status: accepted
Date: 2026-05-02
Owner: inventory-team

## Context

Reservations were previously validated downstream, in the fulfilment service.
Oversells surfaced hours later as failed shipments.

## Decision

reserve() must reject a reservation that exceeds available stock. The check
belongs at the point of reservation, not downstream.

## Consequences

Any change to reserve() that removes the stock comparison is a defect, not a
refactor. The functional gate encodes this as test_reserve_rejects_oversell.
