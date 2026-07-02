#!/usr/bin/env python3
"""
Internet Connection Quality Checker
-----------------------------------
A Python 3 script to verify internet connectivity, measure latency,
and evaluate connection quality (DNS, TCP, and HTTP).
Outputs results to the console and logs to a file.
"""

import argparse
import datetime
import logging
import os
import socket
import subprocess
import sys
import time
import urllib.request
import urllib.error

def get_daily_log_path(base_path):
    """Inserts the current date (YYYY-MM-DD) into the log file name."""
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    dirname, filename = os.path.split(base_path)
    name, ext = os.path.splitext(filename)
    
    # If the date is already in the name, don't double add it
    if today_str in name:
        return base_path
        
    new_filename = f"{name}_{today_str}{ext}"
    return os.path.join(dirname, new_filename)

import json

# Load parameters from external file
PARAMETERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parameters.json")
try:
    with open(PARAMETERS_FILE, "r") as f:
        _config = json.load(f)
except Exception as e:
    print(f"Error loading {PARAMETERS_FILE}: {e}")
    sys.exit(1)

DEFAULT_TEST_TARGETS = _config.get("test_targets", [])
DEFAULT_LOG_FILE = _config.get("default_log_file", "connection_check.log")
DEFAULT_TIMEOUT = _config.get("default_timeout", 3.0)
DEFAULT_INTERVAL = _config.get("default_interval", 10.0)

# Set up logging formatting
class CustomFormatter(logging.Formatter):
    """Custom formatter to provide clear, human-readable logging logs."""
    
    # ANSI color codes for premium terminal feel
    GREY = "\x1b[38;20m"
    CYAN = "\x1b[36;20m"
    GREEN = "\x1b[32;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"
    
    def __init__(self, use_color=True):
        super().__init__()
        self.use_color = use_color
        
        # Format string for logs
        self.fmt = "%(asctime)s - [%(levelname)s] - %(message)s"
        self.date_fmt = "%Y-%m-%d %H:%M:%S"
        
        # Mapping log level to color
        self.FORMATS = {
            logging.DEBUG: self.GREY + self.fmt + self.RESET,
            logging.INFO: self.CYAN + self.fmt + self.RESET,
            logging.WARNING: self.YELLOW + self.fmt + self.RESET,
            logging.ERROR: self.RED + self.fmt + self.RESET,
            logging.CRITICAL: self.BOLD_RED + self.fmt + self.RESET
        }

    def format(self, record):
        if self.use_color and record.levelno in self.FORMATS:
            log_fmt = self.FORMATS[record.levelno]
        else:
            log_fmt = self.fmt
            
        formatter = logging.Formatter(log_fmt, datefmt=self.date_fmt)
        return formatter.format(record)


def setup_logger(log_file_base, verbose=False):
    """Sets up console and file logging. Automatically inserts current date in file name."""
    logger = logging.getLogger("ConnectionChecker")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Resolve the date-based file path
    log_file_path = get_daily_log_path(log_file_base)
    
    # Check if we already have handlers to avoid duplication or rotate dynamically
    has_console = False
    file_handler_to_remove = None
    
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
            has_console = True
        elif isinstance(handler, logging.FileHandler):
            # If the path matches, we keep it; otherwise we rotate/replace it
            if os.path.abspath(handler.baseFilename) == os.path.abspath(log_file_path):
                pass
            else:
                file_handler_to_remove = handler

    # Remove old file handler if it exists and path doesn't match
    if file_handler_to_remove:
        file_handler_to_remove.close()
        logger.removeHandler(file_handler_to_remove)

    # Console Handler (colored if stdout is a TTY)
    if not has_console:
        use_color = sys.stdout.isatty()
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(CustomFormatter(use_color=use_color))
        console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
        logger.addHandler(console_handler)

    # File Handler (no ANSI colors, structured format)
    has_correct_file_handler = any(
        isinstance(h, logging.FileHandler) and os.path.abspath(h.baseFilename) == os.path.abspath(log_file_path)
        for h in logger.handlers
    )
    
    if not has_correct_file_handler:
        file_formatter = logging.Formatter(
            "%(asctime)s - [%(levelname)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        try:
            file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(logging.DEBUG)
            logger.addHandler(file_handler)
        except IOError as e:
            logger.error(f"Failed to set up log file at {log_file_path}: {e}")
            
    return logger, log_file_path


def check_dns_resolution(host, timeout):
    """Measures the time taken to resolve a host to an IP address."""
    start_time = time.perf_counter()
    try:
        socket.gethostbyname(host)
        duration_ms = (time.perf_counter() - start_time) * 1000
        return True, duration_ms
    except socket.gaierror:
        return False, 0.0


def check_tcp_connection(host, port, timeout):
    """Measures the TCP connection handshake latency to a given host and port."""
    start_time = time.perf_counter()
    try:
        # Create a socket and attempt to connect
        with socket.create_connection((host, port), timeout=timeout) as sock:
            duration_ms = (time.perf_counter() - start_time) * 1000
            return True, duration_ms
    except (socket.timeout, OSError):
        return False, 0.0


def check_http_request(url, timeout):
    """Measures HTTP GET response latency."""
    start_time = time.perf_counter()
    try:
        # Create request with a browser user-agent to avoid potential bot blocks
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ConnectionQualityChecker/1.0'}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            _ = response.read(1024)  # Read initial chunk to ensure full header response
            duration_ms = (time.perf_counter() - start_time) * 1000
            return True, duration_ms, response.status
    except urllib.error.URLError as e:
        return False, 0.0, getattr(e, 'code', 'URLError')
    except socket.timeout:
        return False, 0.0, 'Timeout'
    except Exception as e:
        return False, 0.0, type(e).__name__


def evaluate_connection(targets, timeout, logger):
    """Performs all connectivity tests and returns a summary status."""
    logger.info("Starting internet connection diagnostics...")
    
    successful_tests = 0
    total_tests = 0
    latencies = []
    
    # 1. DNS Resolution Check
    dns_targets = [t for t in targets if t.get("type") == "web_server"]
    for target in dns_targets:
        total_tests += 1
        resolved, duration = check_dns_resolution(target["host"], timeout)
        if resolved:
            successful_tests += 1
            logger.debug(f"DNS Resolution: Resolved {target['host']} successfully in {duration:.1f}ms")
        else:
            logger.warning(f"DNS Resolution: Failed to resolve {target['host']}")

    # 2. TCP Port Connection Check
    for target in targets:
        total_tests += 1
        connected, duration = check_tcp_connection(target["host"], target["port"], timeout)
        if connected:
            successful_tests += 1
            latencies.append(duration)
            logger.debug(f"TCP Connect: Connected to {target['name']} ({target['host']}:{target['port']}) in {duration:.1f}ms")
        else:
            logger.warning(f"TCP Connect: Failed to connect to {target['name']} ({target['host']}:{target['port']})")

    # 3. HTTP GET request Check
    http_targets = [t for t in targets if "url" in t]
    for target in http_targets:
        total_tests += 1
        success, duration, status = check_http_request(target["url"], timeout)
        if success:
            successful_tests += 1
            latencies.append(duration)
            logger.debug(f"HTTP GET: Loaded {target['url']} (Status: {status}) in {duration:.1f}ms")
        else:
            logger.warning(f"HTTP GET: Failed to load {target['url']} (Status/Error: {status})")

    # Analyze overall results
    success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
    
    logger.info(f"Diagnostics completed. Success rate: {success_rate:.1f}% ({successful_tests}/{total_tests} checks passed)")
    if latencies:
        logger.info(f"Average connection latency: {avg_latency:.1f}ms")
    
    # Interpret connection quality
    if success_rate == 100:
        if avg_latency < 50:
            quality = "EXCELLENT (Very low latency, 100% reliable)"
            log_level = logging.INFO
        elif avg_latency < 150:
            quality = "GOOD (Normal latency, 100% reliable)"
            log_level = logging.INFO
        else:
            quality = "FAIR (High latency, but reliable connection)"
            log_level = logging.WARNING
    elif success_rate >= 70:
        quality = "DEGRADED (Some tests failed or timed out)"
        log_level = logging.WARNING
    elif success_rate > 0:
        quality = "POOR (Significant connection issues, packet loss detected)"
        log_level = logging.ERROR
    else:
        quality = "NO INTERNET (All checks failed)"
        log_level = logging.CRITICAL

    logger.log(log_level, f"Overall Internet Connection Status: {quality}")
    return success_rate, avg_latency, quality


def update_gpio(success_rate, logger):
    """Updates the GPIO status using gpio_control.py based on connection success."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    gpio_script = os.path.join(script_dir, "gpio_control.py")
    
    # In case of fail (0.0 success rate), turn OFF. In case of success, turn ON.
    state = "on" if success_rate > 0 else "off"
    try:
        subprocess.run([sys.executable, gpio_script, "17", state], check=True, capture_output=True, text=True)
        logger.debug(f"GPIO 17 set to {state.upper()} via gpio_control.py")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to call gpio_control.py: {e.stderr.strip() if e.stderr else e}")
    except Exception as e:
        logger.error(f"Failed to call gpio_control.py: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Verify internet connectivity and evaluate connection quality."
    )
    parser.add_argument(
        "--log-file", 
        default=DEFAULT_LOG_FILE,
        help=f"Path to the log file (default: {DEFAULT_LOG_FILE})"
    )
    parser.add_argument(
        "--timeout", 
        type=float, 
        default=DEFAULT_TIMEOUT,
        help=f"Timeout in seconds for each network test (default: {DEFAULT_TIMEOUT})"
    )
    parser.add_argument(
        "--loop", 
        action="store_true",
        help="Run connection tests continuously in a loop"
    )
    parser.add_argument(
        "--interval", 
        type=float, 
        default=DEFAULT_INTERVAL,
        help=f"Interval in seconds between tests when running in loop mode (default: {DEFAULT_INTERVAL})"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable detailed debugging messages in the console"
    )
    
    args = parser.parse_args()

    # Set up logger
    logger, active_log_file = setup_logger(args.log_file, args.verbose)
    
    if args.loop:
        logger.info(f"Starting continuous connection checker. Press Ctrl+C to stop.")
        logger.info(f"Testing every {args.interval} seconds. Logging details to {active_log_file}")
        try:
            last_date = datetime.date.today()
            while True:
                # Rotate the log file if midnight has passed
                current_date = datetime.date.today()
                if current_date != last_date:
                    logger, active_log_file = setup_logger(args.log_file, args.verbose)
                    logger.info(f"Day changed. Switched logging to new file: {active_log_file}")
                    last_date = current_date
                
                success_rate, _, _ = evaluate_connection(DEFAULT_TEST_TARGETS, args.timeout, logger)
                update_gpio(success_rate, logger)
                print("-" * 60)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            logger.info("Checker stopped by user.")
    else:
        success_rate, _, _ = evaluate_connection(DEFAULT_TEST_TARGETS, args.timeout, logger)
        update_gpio(success_rate, logger)
        logger.info(f"Detailed logs saved to {active_log_file}")


if __name__ == "__main__":
    main()
