# DAV Framework v3

Production-grade streaming Retail POS processing framework.

## Key Features

- Streaming architecture (constant memory)
- Configuration-driven parsing
- Supports large files (200MB to 60GB+)
- Polars-based processing
- Strict separation of concerns
- Validator-based reporting

## Architecture Overview

Reader → Detector → Tokenizer → Transaction Builder → Flattener → Mapper → Validator

## Principles

- No full file loading
- No pandas
- No global state
- Fully typed
- SOLID design

## Getting Started

```bash
pip install -e .
pytest