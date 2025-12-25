import json
import logging
import os
import threading
import time
from contextlib import contextmanager
from logging import Logger
from pathlib import Path
from typing import Any

import psutil


@contextmanager
def monitor_resources(logger: Logger, poll_interval: float = 0.01):
    """Context manager to monitor time and peak memory usage."""
    process = psutil.Process(os.getpid())
    peak_rss: float = 0.0
    stop_event = threading.Event()

    def monitor():
        nonlocal peak_rss
        while not stop_event.is_set():
            rss = process.memory_info().rss
            peak_rss = max(peak_rss, rss)
            time.sleep(poll_interval)

    monitor_thread = threading.Thread(target=monitor, daemon=True)
    monitor_thread.start()
    start_time: float = time.time()

    try:
        yield
    finally:
        stop_event.set()
        monitor_thread.join()
        elapsed_time: float = time.time() - start_time
        logger.info("Peak RSS: %.2f MB", peak_rss / 1024**2)
        logger.info("Processing completed. Time taken: %.2f seconds", elapsed_time)


def save_text_to_file(text: str, output_path: Path) -> None:
    """Save text content to a file in the specified output path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text)


def load_json_config(config_path: Path) -> dict[str, Any]:
    """Load configuration from JSON file."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as fh:
        config: dict[str, Any] = json.load(fh)
        return config


def setup_logger(logger: Logger, output_path: Path) -> None:
    """Set up the logger for the application."""
    handler = logging.FileHandler(
        filename=output_path,
        mode="w",
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
