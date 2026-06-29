🧠 Overview
DAV Framework v2 is a streaming retail POS processing framework designed to process files from 200MB to 60GB+ with constant memory usage.

🧱 System Architecture
✅ Parser Pipeline
Reader
↓
Tokenizer
↓
TransactionBuilder
↓
SchemaMapper
↓
SchemaRow (stream)


✅ Validation Pipeline
SchemaRow
↓
ValidationManager
↓
Validators (parallel)
↓
Reports


🔁 Sequence Flow
ParserService.parse(file)
    ↓
ParserEngine
    ↓
Reader → yields lines
    ↓
Tokenizer → yields tokens
    ↓
TransactionBuilder → yields Transaction
    ↓
SchemaMapper → yields SchemaRow
    ↓
ValidationManager → processes rows


📦 Responsibility Separation

Component           Responsibility
Reader              Raw file streaming
Tokenizer           Line → structured token
TransactionBuilder  Group tokens → Transaction
SchemaMapper        Transaction → business schema
Validator           Business rule processing
ValidationManager   Dispatch & aggregation

✅ Key Principles

Streaming (O(1) memory)
Config-driven (no retailer code)
Strict separation of concerns
Dependency Injection everywhere
Fully testable units
Immutable data objects


🔒 Constraints

No pandas
No global state
No cross-layer logic leakage
Parser does NOT know validators
Validators do NOT know parsing structure


✅ ✅ OPTIONAL (Recommended)
📁 Add Diagram Section (Minimal ASCII)
          ┌─────────────┐
          │  Reader     │
          └─────┬───────┘
                ↓
          ┌─────────────┐
          │ Tokenizer   │
          └─────┬───────┘
                ↓
          ┌─────────────┐
          │ Builder     │
          └─────┬───────┘
                ↓
          ┌─────────────┐
          │ Mapper      │
          └─────┬───────┘
                ↓
          ┌─────────────┐
          │ SchemaRow   │
          └─────┬───────┘
                ↓
         ┌───────────────┐
         │ Validators    │
         └───────────────┘

