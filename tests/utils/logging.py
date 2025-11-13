from __future__ import annotations

import logging
from pathlib import Path

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%H:%M:%S"
LOGGER_NAME = "hexlet.kanban"


def configure_logging(level: str, log_dir: Path | None = None) -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)

    if logger.handlers:
        # Logger already configured – update level only.
        logger.setLevel(level)
        return logger

    logger.setLevel(level)

    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "pytest.log", mode="w", encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

    # Keep propagation enabled so that pytest's log capture/CLI handlers work.
    return logger


__all__ = ["configure_logging", "LOGGER_NAME", "LOG_FORMAT", "LOG_DATE_FORMAT"]

