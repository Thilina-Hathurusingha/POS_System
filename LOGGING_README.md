# Logging System Documentation

## Overview
A comprehensive logging system has been added to the POS application with three log levels and colored console output for better readability.

## Log Levels

### 1. **ERROR Level** (Default)
- **Shows**: Only errors
- **Use case**: Production environment - minimal log output
- **Color**: Red

### 2. **WARNING Level**
- **Shows**: All ERROR and WARNING logs
- **Use case**: Staging/Testing - catch potential issues early
- **Color**: RED for errors, YELLOW for warnings

### 3. **DEBUG Level**
- **Shows**: All logs (DEBUG, INFO, WARNING, ERROR)
- **Use case**: Development - detailed visibility into application flow
- **Color**: CYAN for debug info, GREEN for info, YELLOW for warnings, RED for errors

## How to Use

### Method 1: Environment Variable (Recommended)
Set the `LOG_LEVEL` environment variable before running the application:

**Windows (PowerShell):**
```powershell
$env:LOG_LEVEL = "DEBUG"
python main.py
```

**Windows (Command Prompt):**
```cmd
set LOG_LEVEL=DEBUG
python main.py
```

**Linux/Mac:**
```bash
export LOG_LEVEL=DEBUG
python main.py
```

### Method 2: Programmatically in Code
In `main.py`, you can also set the log level directly:

```python
from logging_config import AppLogger

# Set log level before creating the app
AppLogger.setup(log_level='DEBUG')

# Then create and run the app
app = MainApp()
app.mainloop()
```

### Method 3: Change Log Level at Runtime
```python
from logging_config import AppLogger

# Change log level while app is running
AppLogger.set_level('WARNING')
```

## Log Contents

### Entry/Exit Logs
Each function logs its entry and exit points at **DEBUG** level:
```
DEBUG [12:34:56] MainApp.__init__() - ENTRY
DEBUG [12:34:57] MainApp.__init__() - EXIT: Success
```

### Contextual Logs
Additional logs provide information about what's happening:
```
DEBUG [12:34:58] Configuring window properties...
DEBUG [12:34:59] Data processor thread started successfully
INFO  [12:35:00] POS System started successfully
```

### Warning Logs
When there's a possibility of error:
```
WARNING [12:35:15] Page number 10 out of range [1, 5]. Using page 5
WARNING [12:35:20] Data processor not available, skipping initial data load
WARNING [12:35:25] Checkout attempted with empty order
```

### Error Logs
When errors occur:
```
ERROR [12:35:30] Failed to initialize MainApp: Connection timeout
ERROR [12:35:35] Failed to load initial data: NoneType error
```

## Colored Output Examples

**DEBUG Mode** - Shows all levels with colors:
```
[2026-04-13 12:34:56] [DEBUG] main - ENTRY: MainApp.__init__()
[2026-04-13 12:34:57] [INFO] main - POS System started successfully
[2026-04-13 12:35:00] [WARNING] data_processor - Query timeout, retrying...
[2026-04-13 12:35:05] [ERROR] sale_page - Failed to add product to cart
```

**WARNING Mode** - Shows warnings and errors only:
```
[2026-04-13 12:35:00] [WARNING] data_processor - Query timeout, retrying...
[2026-04-13 12:35:05] [ERROR] sale_page - Failed to add product to cart
```

**ERROR Mode** - Shows only errors:
```
[2026-04-13 12:35:05] [ERROR] sale_page - Failed to add product to cart
```

## Files Modified

### Core Logging
- **`logging_config.py`** - New file with logging configuration

### Application Files with Logging Added
- `main.py` - Main application initialization and window management
- `data_processor.py` - Background data processing thread
- `sale_page.py` - Sales interface and order management
- `sale/filters.py` - Product filtering panel
- `sale/products.py` - Product card display
- `sale/table.py` - Order items table
- `sale/navigation.py` - Pagination controls
- `sale/checkout.py` - Checkout and payment summary

## Log Types in Each File

### main.py
- Window initialization and configuration
- Menu bar creation
- Page switching and navigation
- Data queue processing
- Application lifecycle (startup/shutdown)

### data_processor.py
- Thread initialization and startup
- Dummy data creation
- Product pagination and filtering
- Background thread operations
- Data queue messaging

### sale_page.py
- Layout creation
- Filter changes and product refresh
- Page navigation
- Product selection and order management
- Order calculations and checkout validation
- Transaction processing

### sale/filters.py, products.py, table.py, navigation.py, checkout.py
- UI component initialization
- User interactions
- State changes
- Data updates

## Tips for Debugging

1. **Start with ERROR level** - Get baseline error messages
2. **Upgrade to WARNING level** - Catch potential issues
3. **Use DEBUG level** - Trace exact flow of execution
4. **Timestamp tracking** - Correlate events across modules
5. **Search logs** - Use grep to find specific operations

Example:
```bash
python main.py 2>&1 | grep "product"  # Find all product-related logs
python main.py 2>&1 | grep "ERROR"    # Find only errors
```

## Performance Notes

- **DEBUG mode** may have slight performance impact due to extensive logging
- **ERROR/WARNING modes** have minimal performance impact
- Logs are buffered and written efficiently
- Optional file logging can be configured for persistence

## Future Enhancements

You can extend logging by:
1. Adding file output: `AppLogger.setup(log_level='DEBUG', log_file='app.log')`
2. Configuring log rotation: Built-in support already exists
3. Adding custom loggers: `logger = get_logger(__name__)`
4. Creating log levels for specific modules

## Example Usage Scenarios

### Scenario 1: Production Environment
```bash
# Default ERROR level - minimal output
python main.py
```

### Scenario 2: Staging Environment
```bash
# Monitor potential issues
$env:LOG_LEVEL = "WARNING"
python main.py
```

### Scenario 3: Development / Bug Investigation
```bash
# Full visibility into execution flow
$env:LOG_LEVEL = "DEBUG"
python main.py >logs.txt 2>&1  # Capture to file if needed
```

## Color Legend

| Color  | Level   | Meaning |
|--------|---------|---------|
| Red    | ERROR   | Critical issue that needs attention |
| Yellow | WARNING | Potential issue, may need investigation |
| Cyan   | DEBUG   | Detailed execution information |
| Green  | INFO    | Important informational message |
| Gray   | TIME    | Timestamp information |

---

**Happy debugging!** 🚀
