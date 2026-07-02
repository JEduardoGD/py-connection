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
  - **Daily-Based Log File**: Generates structured, timestamped logs in a local log file that automatically embeds the current date (e.g., `connection_check_YYYY-MM-DD.log`).
- **CLI Options**: Supports custom timeouts, custom log files (which will also append the date), and verbose outputs.

## Configuration

The script loads its default settings and testing targets from `parameters.json`. You can modify this file to:
- Change the target servers (DNS or HTTP) that the script tests.
- Update the default timeout for the tests.
- Change the default base name for the log file.

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

## CLI Reference

```text
usage: check_connection.py [-h] [--log-file LOG_FILE] [--timeout TIMEOUT] [--verbose]

Verify internet connectivity and evaluate connection quality.

options:
  -h, --help           show this help message and exit
  --log-file LOG_FILE  Path to the log file (default: connection_check.log)
  --timeout TIMEOUT    Timeout in seconds for each network test (default: 3.0)
  --verbose            Enable detailed debugging messages in the console
```
