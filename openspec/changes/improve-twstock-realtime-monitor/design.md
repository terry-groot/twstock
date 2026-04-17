## Context

The current implementation has two separate monitor scripts (`twstock_monitor.py` and `futures_monitor.py`) with significant code duplication. Both fetch market data, check alerts, render terminal UI, and manage configuration independently. This creates maintenance burden: bugs must be fixed twice, features must be implemented twice, and changes to one often necessitate parallel changes to the other.

Key constraints:
- Must work on Windows, macOS, and Linux
- Terminal-based UI must remain responsive and clear
- API reliability is critical (Taifex API is rate-limited, TWSE API occasionally fails)
- Configuration should be user-editable JSON
- UTF-8 and CJK character display must work correctly

## Goals / Non-Goals

**Goals:**
- Reduce code duplication by extracting common patterns into reusable modules
- Improve resilience through better error handling and retry logic
- Enable easier testing via dependency injection and modular design
- Support multiple data sources through a plugin architecture
- Add structured logging for debugging
- Maintain backward compatibility with existing configuration format (with migration path)
- Improve code maintainability and reduce cognitive load

**Non-Goals:**
- Complete rewrite of the UI (maintain similar terminal output)
- Adding web-based dashboard (stays terminal-only)
- Real-time push notifications (stays polling-based)
- Support for additional markets beyond TWSE/Taifex
- Database persistence of historical data

## Decisions

### 1. Modular Architecture with Plugin System
**Decision:** Create a plugin-based architecture where data sources are interchangeable components.

**Rationale:** Allows adding new data sources (e.g., crypto markets, other stock exchanges) without modifying core monitoring logic. Each plugin implements a consistent interface: `get_data(contract_ids) -> Dict[str, AssetData]`

**Alternatives considered:**
- Monolithic refactor: simpler short-term but harder to extend
- Microservices: overkill for a CLI tool
- **Selected: Plugin system** - balance between flexibility and simplicity

### 2. Configuration Structure
**Decision:** Unify both monitors into a single `monitor_config.json` that supports both `stocks` and `futures` arrays with consistent schema.

**Rationale:** Users can manage one file instead of two. Configuration is validated at startup. Same schema for both types makes shared code easier.

**Schema:**
```json
{
  "stocks": [
    {"id": "2330", "name": "台積電", "upper": 1000, "lower": 900, "enabled": true}
  ],
  "futures": [
    {"id": "TX", "name": "台指期", "upper": 34000, "lower": 32000, "enabled": true}
  ],
  "monitor": {
    "stock_interval": 5,
    "futures_interval": 30,
    "retry_max_attempts": 3,
    "retry_backoff_seconds": 2
  }
}
```

**Alternatives considered:**
- Keep separate config files: no benefit, adds complexity
- YAML format: less familiar to Python beginners
- **Selected: Unified JSON** - familiar, easy to edit, schema-validatable

### 3. Error Handling Strategy
**Decision:** Implement three-tier error handling:
1. **Transient errors** (network timeout, rate limit): retry with exponential backoff
2. **Persistent errors** (invalid contract code): skip asset, log warning, continue
3. **Critical errors** (configuration invalid, all APIs down): fail fast with clear message

**Rationale:** Distinguishing error types prevents hammering failing APIs while recovering from temporary issues. Graceful degradation improves user experience.

**Alternatives considered:**
- Retry all errors: can lead to infinite loops on configuration errors
- Fail on first error: too fragile for unreliable networks
- **Selected: Tiered approach** - balances robustness with fail-fast principles

### 4. Shared Utilities Module Structure
**Decision:** Create `market_monitor/` package with:
- `core.py`: Base classes (`DataSource`, `Monitor`)
- `sources/`: Data source implementations (`stocks.py`, `futures.py`)
- `utils.py`: Common functions (CJK formatting, price parsing, alert logic)
- `ui.py`: Terminal rendering
- `config.py`: Configuration loading and validation
- `logging.py`: Structured logging setup

**Rationale:** Clear separation of concerns makes code easier to test and reuse. Each module has a single responsibility.

**Alternatives considered:**
- Single large module: hard to navigate and test
- Too many small files: overhead of imports
- **Selected: 6 focused modules** - good balance

### 5. Testing Strategy
**Decision:** Unit tests for utilities and parsing, integration tests for data sources using mock APIs.

**Rationale:** Core logic (alert checking, parsing) is deterministic and easy to unit test. Data source integration benefits from realistic mocking to avoid API dependency during CI/CD.

**Tool:** pytest with fixtures for mock API responses

### 6. Backwards Compatibility Migration
**Decision:** At startup, detect old config format and automatically migrate to new format, backing up original.

**Rationale:** Users with existing setups won't break. Migration is transparent.

**Implementation:** Check for `config.json` and `futures_config.json`, merge them if found, prompt user if conflicts.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| **Plugin system adds complexity** | Start with simple interface, document with examples |
| **Unified config could confuse new users** | Provide clear migration guide and default template |
| **Retry logic might mask real failures** | Log all retries, provide diagnostics in verbose mode |
| **CJK column alignment is fragile** | Comprehensive tests for all character width edge cases |
| **API rate limits still cause gaps** | Document rate limits, show degraded UI when throttled |
| **Breaking change for users with scripts** | Maintain old monitor scripts as deprecated alternatives during transition |

## Open Questions

1. **Should old monitor scripts be removed or kept as deprecated wrappers?** → Decision: Keep for 1 release cycle, clearly mark as deprecated
2. **What logging output should go to console vs. log file?** → Decision: Errors to console, all activity to optional log file
3. **Should we validate API credentials/keys at startup?** → Decision: No, not applicable for TWSE/Taifex (public APIs)
