"""Functions to set up logging with noise suppression for distributed workloads (e.g., Dask, Tornado).

Functions:
    - `setup_logging`: Configure logging with custom formatting and noise suppression.
    - `CustomLoggingFormatter`: Custom formatter to map ERROR→SEVERE and CRITICAL→FATAL without mutating log records.
    - `NoisyDistributedFilter`: Filter to suppress noisy Dask/Tornado connection and heartbeat errors.
    - `StderrFilter`: Filter to suppress noisy stderr output that bypasses logging (e.g., in MPI/SLURM environments).

"""

import logging
import sys
from pathlib import Path
from typing import Optional, Union


class CustomLoggingFormatter(logging.Formatter):
    """Map ERROR→SEVERE and CRITICAL→FATAL without mutating log records."""

    LEVEL_MAP = {
        logging.ERROR: "SEVERE",
        logging.CRITICAL: "FATAL",
    }

    def format(self, record: logging.LogRecord) -> str:
        original = record.levelname
        record.levelname = self.LEVEL_MAP.get(record.levelno, original)
        try:
            return super().format(record)
        finally:
            record.levelname = original  # restore to avoid side effects


class NoisyDistributedFilter(logging.Filter):
    """Filter noisy Dask/Tornado connection + heartbeat errors."""

    IGNORED_KEYWORDS = (
        "Failed to communicate with scheduler during heartbeat",
        "CommClosedError",
        "StreamClosedError",
        "distributed.comm.core.CommClosedError",
        "tornado.iostream.StreamClosedError",
    )

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()

        if any(k in msg for k in self.IGNORED_KEYWORDS):
            return False

        if record.exc_info:
            exc_text = logging.Formatter().formatException(record.exc_info)
            if any(k in exc_text for k in self.IGNORED_KEYWORDS):
                return False

        return True


class StderrFilter:
    """Filter stderr output that bypasses logging (e.g., MPI/SLURM environments)."""

    IGNORED_KEYWORDS = NoisyDistributedFilter.IGNORED_KEYWORDS

    def write(self, msg: str):
        if not any(k in msg for k in self.IGNORED_KEYWORDS):
            sys.__stderr__.write(msg)

    def flush(self):
        sys.__stderr__.flush()


def setup_logging(
    level: Union[int, str] = logging.INFO,
    log_file: Optional[Union[str, Path]] = None,
    file_level: Optional[Union[int, str]] = None,
    filter_stderr: bool = False,
):
    """Configure logging with noise suppression for distributed workloads.

    Args:
        level (int | str): Logging level for console output (default: logging.INFO).
        log_file (str | Path, optional): Optional path to a log file for file output.
        file_level (int | str, optional): Optional logging level for file output (defaults to console level if not provided).
        filter_stderr (bool, optional): If True, redirect sys.stderr to a filter that suppresses noisy output (use with caution).

    Returns:
        None. Configures logging globally.

    Note: Enabling stderr filtering can suppress important error messages from libraries that write directly to stderr. Use with caution and consider the implications for debugging and monitoring in production environments.

    """
    # Normalize log levels
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "warn": logging.WARNING,
        "error": logging.ERROR,
        "severe": logging.ERROR,
        "fatal": logging.CRITICAL,
        "critical": logging.CRITICAL,
    }

    if isinstance(level, str):
        level = level_map.get(level.lower(), logging.INFO)

    if isinstance(file_level, str):
        file_level = level_map.get(file_level.lower(), level)

    file_level = file_level or level

    # Root logger setup
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    formatter = CustomLoggingFormatter(
        "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s"
    )

    noise_filter = NoisyDistributedFilter()

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(formatter)
    console.addFilter(noise_filter)
    root.addHandler(console)

    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path, mode="w")
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(noise_filter)

        root.addHandler(file_handler)

    # Suppress noisy libraries
    noisy_loggers = {
        "google.auth.compute_engine._metadata": logging.ERROR,
        "fsspec.reference": logging.WARNING,
        "distributed": logging.WARNING,
        "distributed.worker": logging.WARNING,
        "distributed.comm": logging.ERROR,
        "dask": logging.WARNING,
        "tornado": logging.ERROR,
        "botocore": logging.WARNING,
    }

    for name, lvl in noisy_loggers.items():
        logging.getLogger(name).setLevel(lvl)

    # Optional stderr filtering
    if filter_stderr:
        sys.stderr = StderrFilter()
