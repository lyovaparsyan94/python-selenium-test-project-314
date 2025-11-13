from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .constants import IMPLICIT_WAIT, PAGE_LOAD_TIMEOUT, WINDOW_SIZE


@dataclass(frozen=True, slots=True)
class TestConfig:
    base_url: str
    log_level: str
    log_dir: Path
    headless: bool
    window_size: str
    page_load_timeout: int
    implicit_wait: float


def _resolve_path(value: str) -> Path:
    path = Path(value)
    try:
        return path.resolve()
    except OSError:
        # Fallback to absolute path joined with cwd if resolve() fails (e.g. path not yet created)
        return Path.cwd() / path


def load_config() -> TestConfig:
    base_url = os.getenv("APP_BASE_URL")
    if not base_url:
        raise RuntimeError("APP_BASE_URL environment variable must be set")

    log_level = os.getenv("TEST_LOG_LEVEL", "INFO").upper()
    log_dir = _resolve_path(os.getenv("TEST_LOG_DIR", "code/.logs"))
    headless = os.getenv("HEADLESS", "true").lower() not in {"false", "0", "no"}
    window_size = os.getenv("BROWSER_WINDOW_SIZE", WINDOW_SIZE)
    page_load_timeout = int(os.getenv("PAGE_LOAD_TIMEOUT", str(PAGE_LOAD_TIMEOUT)))
    implicit_wait = float(os.getenv("SELENIUM_IMPLICIT_WAIT", str(IMPLICIT_WAIT)))

    return TestConfig(
        base_url=base_url,
        log_level=log_level,
        log_dir=log_dir,
        headless=headless,
        window_size=window_size,
        page_load_timeout=page_load_timeout,
        implicit_wait=implicit_wait,
    )


__all__ = ["TestConfig", "load_config"]

