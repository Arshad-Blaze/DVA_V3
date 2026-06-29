---

# ✅ `Architecture.md`

```markdown
# DAV Framework v2 Architecture

## Pipeline

Reader
↓
Detector
↓
Tokenizer
↓
Transaction Builder
↓
Flattener
↓
Mapper
↓
Transaction

## Streaming Principle

- Each transaction is processed and discarded
- No large in-memory datasets
- Validators maintain aggregates only

## Core Contracts

### Parser
- Emits Transaction objects only
- No validation logic

### Validators
- Stateless per transaction
- Stateful aggregates only

### Configuration
- YAML-driven
- No retailer-specific logic in code