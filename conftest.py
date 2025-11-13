from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%H:%M:%S"
LOGGER_NAME = "hexlet.kanban"

DEFAULT_HEADLESS = os.getenv("HEADLESS", "true").lower() not in {"false", "0", "no"}
DEFAULT_WINDOW_SIZE = os.getenv("BROWSER_WINDOW_SIZE", "1440,900")
DEFAULT_PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", "45"))
DEFAULT_IMPLICIT_WAIT = float(os.getenv("SELENIUM_IMPLICIT_WAIT", "0.2"))
DEFAULT_LOG_LEVEL = os.getenv("TEST_LOG_LEVEL", "INFO").upper()
DEFAULT_LOG_DIR = Path(os.getenv("TEST_LOG_DIR", "test-results")).resolve()


@dataclass(frozen=True, slots=True)
class TestConfig:
    implementation: str | None
    base_url: str
    log_level: str
    log_dir: Path
    screenshots_dir: Path
    headless: bool
    window_size: str
    page_load_timeout: int
    implicit_wait: float


def configure_logging(level: str, log_dir: Path | None = None) -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)

    if logger.handlers:
        logger.setLevel(level)
        return logger

    logger.setLevel(level)

    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "pytest.log", mode="w", encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

    return logger

def load_config() -> TestConfig:
    implementation = os.getenv("IMPLEMENTATION")

    if implementation:
        base_url = f"http://{implementation}.test"
        os.environ["APP_BASE_URL"] = base_url
        descriptor = implementation
    else:
        base_url = os.getenv("APP_BASE_URL")
        if not base_url:
            message = (
                "APP_BASE_URL is not set. "
                "For local runs provide APP_BASE_URL (e.g. http://127.0.0.1:5173) "
                "or use IMPLEMENTATION for prebuilt fixtures."
            )
            raise RuntimeError(message)
        parsed = urlparse(base_url)
        descriptor = parsed.hostname or "custom"

    log_dir = DEFAULT_LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)

    screenshots_dir = log_dir / "screenshots" / descriptor
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    return TestConfig(
        implementation=implementation,
        base_url=base_url,
        log_level=DEFAULT_LOG_LEVEL,
        log_dir=log_dir,
        screenshots_dir=screenshots_dir,
        headless=DEFAULT_HEADLESS,
        window_size=DEFAULT_WINDOW_SIZE,
        page_load_timeout=DEFAULT_PAGE_LOAD_TIMEOUT,
        implicit_wait=DEFAULT_IMPLICIT_WAIT,
    )


def _ensure_basic_logging(level: str) -> None:
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(level=level, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)


@pytest.fixture(scope="session")
def test_config() -> TestConfig:
    return load_config()


@pytest.fixture(scope="session")
def test_logger(test_config: TestConfig) -> logging.Logger:
    _ensure_basic_logging(test_config.log_level)
    logger = configure_logging(test_config.log_level, test_config.log_dir)
    logging.captureWarnings(True)
    logger.info(
        "Logging initialised (implementation=%s, base_url=%s, log_dir=%s)",
        test_config.implementation or "custom",
        test_config.base_url,
        test_config.log_dir,
    )
    return logger


@pytest.fixture(scope="session")
def base_url(test_config: TestConfig) -> str:
    return test_config.base_url


def _configure_options(test_config: TestConfig) -> Options:
    options = Options()
    if test_config.headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument(f"--window-size={test_config.window_size}")
    chrome_binary = os.getenv("CHROME_BIN", "/usr/bin/chromium")
    if Path(chrome_binary).exists():
        options.binary_location = chrome_binary
    return options


def _prepare_driver(driver: webdriver.Chrome, base_url: str) -> None:
    driver.get(base_url)
    driver.delete_all_cookies()
    driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")


def _new_browser(base_url: str, test_config: TestConfig) -> webdriver.Chrome:
    options = _configure_options(test_config)
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(test_config.page_load_timeout)
    driver.implicitly_wait(test_config.implicit_wait)
    _prepare_driver(driver, base_url)
    return driver


def _safe_test_name(nodeid: str) -> str:
    name = nodeid.replace("::", "__").replace("/", "_")
    return re.sub(r"[^\w.-]", "_", name)


def _save_screenshot(
    driver: webdriver.Chrome,
    target_dir: Path,
    nodeid: str,
    logger: logging.Logger,
) -> None:
    filename = f"{_safe_test_name(nodeid)}.png"
    path = target_dir / filename
    try:
        success = driver.save_screenshot(str(path))
    except Exception as error:  # noqa: BLE001
        logger.error("Failed to create screenshot %s: %s", path, error)
        return

    if success:
        logger.info("Saved screenshot to %s", path)
    else:
        logger.warning("Driver did not report success when saving screenshot to %s", path)


@pytest.fixture
def driver(
    base_url: str,
    test_config: TestConfig,
    test_logger: logging.Logger,
    request: pytest.FixtureRequest,
):
    test_logger.debug("Creating new browser instance for %s", request.node.nodeid)
    browser = _new_browser(base_url, test_config)
    try:
        yield browser
    finally:
        outcome = getattr(request.node, "rep_call", None)
        if outcome and outcome.failed:
            _save_screenshot(
                browser,
                test_config.screenshots_dir,
                request.node.nodeid,
                test_logger,
            )
        test_logger.debug("Closing browser instance for %s", request.node.nodeid)
        browser.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    result = outcome.get_result()
    setattr(item, f"rep_{result.when}", result)
