# Architectural Decisions

## 1. Polars Only

Chosen for performance and lazy execution support.

## 2. Streaming Design

Ensures scalability for files >60GB.

## 3. Dataclass Models

- Type safety
- Immutability support
- Clear contracts

## 4. No DataFrame in Parser

Avoids memory overhead and tight coupling.

## 5. Validator Isolation

Validators operate independently and are pluggable.

## 6. Configuration-Driven System

Retailers onboard via YAML only.
