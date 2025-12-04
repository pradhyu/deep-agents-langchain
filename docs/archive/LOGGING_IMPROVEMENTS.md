# Logging Improvements

## Overview

Replaced print statements with proper Python logging throughout the project for better control, configurability, and professional output.

## Changes Made

### 1. New Logging Utility Module

**File**: `src/deepagents_sample/utils/logger.py`

- `setup_logger()`: Configure loggers with consistent formatting
- `get_logger()`: Get logger instances by name
- Standardized format: `[timestamp] [level] [name] message`

### 2. Middleware Updates

#### LoggingMiddleware (`middleware/logging_middleware.py`)
- ✅ Now uses Python `logging` module instead of `print()`
- ✅ Accepts optional `logger` parameter
- ✅ Supports standard log levels (INFO, DEBUG, WARNING, ERROR)
- ✅ Proper timestamp formatting via logging framework

#### MetricsMiddleware (`middleware/metrics_middleware.py`)
- ✅ `print_summary()` now uses `logger.info()` instead of `print()`
- ✅ Accepts optional `logger` parameter
- ✅ Cleaner, more professional output

### 3. Example Scripts

#### Example 1 (`examples/example1_basic_middleware.py`)
- ✅ Completely refactored to use logging
- ✅ Separate loggers for different components:
  - `example1`: Main example flow
  - `middleware`: Middleware operations
  - `metrics`: Metrics output
- ✅ Proper log levels (INFO, WARNING, DEBUG)
- ✅ No more `print()` statements

### 4. Test Suite

**File**: `test_all_components.py`
- ✅ Uses logging for test output
- ✅ Cleaner test result reporting

## Benefits

### 1. **Configurability**
```python
# Easy to change log levels
logger = setup_logger("myapp", level=logging.DEBUG)

# Can redirect to files
handler = logging.FileHandler('app.log')
logger.addHandler(handler)
```

### 2. **Filtering**
```python
# Show only warnings and errors
logging.basicConfig(level=logging.WARNING)

# Show everything
logging.basicConfig(level=logging.DEBUG)
```

### 3. **Professional Output**
```
Before (print):
Step 1: Creating middleware chain...

After (logging):
[2025-12-01 23:31:32] [INFO] [example1] Step 1: Creating middleware chain...
```

### 4. **Component Separation**
Different loggers for different components:
- `[example1]` - Main example flow
- `[middleware]` - Middleware operations  
- `[metrics]` - Performance metrics
- `[deepagents_sample.tools]` - Tool operations

### 5. **Production Ready**
- Can easily integrate with logging aggregation services
- Supports log rotation
- Can filter by component
- Thread-safe

## Usage Examples

### Basic Usage
```python
from deepagents_sample.utils import setup_logger

# Create a logger
logger = setup_logger("myapp")

# Use it
logger.info("Application started")
logger.warning("Low memory")
logger.error("Connection failed")
```

### With Middleware
```python
from deepagents_sample.middleware import LoggingMiddleware, MetricsMiddleware
from deepagents_sample.utils import setup_logger

# Create custom loggers
middleware_logger = setup_logger("middleware", level=logging.DEBUG)
metrics_logger = setup_logger("metrics", level=logging.INFO)

# Pass to middleware
logging_mw = LoggingMiddleware(verbose=True, logger=middleware_logger)
metrics_mw = MetricsMiddleware(logger=metrics_logger)
```

### Filtering Output
```python
# Only show warnings and errors
import logging
logging.basicConfig(level=logging.WARNING)

# Show everything including debug
logging.basicConfig(level=logging.DEBUG)

# Disable logging for specific component
logging.getLogger("middleware").setLevel(logging.ERROR)
```

## Migration Status

### ✅ Completed
- [x] Logging utility module
- [x] LoggingMiddleware
- [x] MetricsMiddleware  
- [x] Example 1 (basic middleware)
- [x] Test suite

### 🔄 Remaining (Optional)
- [ ] Example 2 (LangGraph subagents)
- [ ] Example 3 (MCP tools)
- [ ] run_all.py
- [ ] Agent classes (if they have print statements)

## Testing

Run Example 1 to see the new logging in action:
```bash
uv run python -m deepagents_sample.examples.example1_basic_middleware
```

Output now includes proper timestamps, log levels, and component names:
```
[2025-12-01 23:31:32] [INFO] [example1] EXAMPLE 1: BASIC MIDDLEWARE USAGE
[2025-12-01 23:31:32] [INFO] [middleware] → REQUEST to agent 'coordinator'
[2025-12-01 23:31:32] [DEBUG] [middleware]   Input: Analyze the current system status
[2025-12-01 23:31:32] [INFO] [metrics] METRICS SUMMARY
```

## Backward Compatibility

The changes are backward compatible:
- Middleware still works without passing a logger (creates default)
- All existing functionality preserved
- Only output format changed (improved)

## Next Steps

To complete the logging migration:
1. Update Example 2 and 3 to use logging
2. Update run_all.py menu system
3. Add logging configuration file support (optional)
4. Add log file output option (optional)

---

**Result**: Professional, configurable, production-ready logging system! 🎉
