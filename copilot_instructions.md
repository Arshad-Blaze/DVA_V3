# Copilot Instructions - DAV Framework v3

## Rules

1. Do NOT change architecture.
2. Implement only one module at a time.
3. Parser must never return DataFrames.
4. No retailer-specific logic.
5. Follow SOLID principles.
6. Fully typed code only.
7. No global state.
8. Prefer extending existing abstractions.

## Workflow

Before coding:
- Inspect project structure
- Reuse existing components
- Avoid duplication

After coding:
- Ensure pytest passes
- Ensure Ruff compliance

## Anti-Patterns

- Loading full files into memory
- Mixing parsing and validation
- Hardcoding retailer logic

## Glossary

Transaction: Core data unit  
Token: Parsed line representation  
Validator: Aggregation unit  