# Internet Connection Quality Checker

A lightweight, robust Python 3 script to verify internet connectivity, measure latency, and evaluate connection quality (DNS, TCP, and HTTP). 

This script doesn't require any third-party library dependencies (it uses only standard Python libraries) and works on any system with Python 3 installed.

## Features

- **Multi-layered diagnostics**:
  - **DNS Resolution**: Resolves target domains to verify DNS lookup speed and reliability.
  - **TCP Connections**: Measures handshake latency to popular hosts on ports `53`, `80`, and `443`.
  - **HTTP Requests**: Performs simple HTTP GET requests to check end-to-end web availability and status codes.
- **Double Logging**:
  - **Console Output**: Uses a premium, clean output format with ANSI color-coding for readability.
  - **Daily-Based Log File**: Generates structured, timestamped logs in a local log file that automatically embeds the current date (e.g., `connection_check_YYYY-MM-DD.log`). Log files automatically rotate at midnight during continuous monitoring.
- **Hardware Integration**: Automatically toggles a configured Raspberry Pi GPIO port (default 17) based on connection status (requires `RPi.GPIO`). The specific GPIO logic states for successful and failed connections are configurable.
- **Continuous Monitoring**: Supports continuous running mode (`--loop`) with a configurable checking interval.
- **CLI Options**: Supports custom timeouts, custom log files, continuous loop, and verbose outputs.

## Configuration

The script loads its default settings and testing targets from `parameters.json`. You can modify this file to:
- Change the target servers (DNS or HTTP) that the script tests.
- Update the default timeout and checking interval for the tests.
- Change the default base name for the log file.
- Configure hardware integration settings, including the GPIO port and the specific logic states for internet success and failure.

## Usage

### Run Once (Default)
To perform a single connection check:
```bash
python check_connection.py
```

### Run with Verbose (Detailed Logs in Console)
To see full diagnostics step-by-step:
```bash
python check_connection.py --verbose
```

### Specify a Custom Log File
```bash
python check_connection.py --log-file my_network_log.log
```

### Run Continuously
To run tests repeatedly at a specific interval (e.g. 10 seconds):
```bash
python check_connection.py --loop --interval 10.0
```

## CLI Reference

```text
usage: check_connection.py [-h] [--log-file LOG_FILE] [--timeout TIMEOUT] [--loop] [--interval INTERVAL] [--verbose]

Verify internet connectivity and evaluate connection quality.

options:
  -h, --help           show this help message and exit
  --log-file LOG_FILE  Path to the log file (default: connection_check.log)
  --timeout TIMEOUT    Timeout in seconds for each network test (default: 3.0)
  --loop               Run connection tests continuously in a loop
  --interval INTERVAL  Interval in seconds between tests when running in loop mode (default: 10.0)
  --verbose            Enable detailed debugging messages in the console
```
