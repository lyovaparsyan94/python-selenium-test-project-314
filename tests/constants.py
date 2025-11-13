import os

USER = {
    "login": "user",
    "password": "password",
}

DEFAULT_TIMEOUT = int(os.getenv("SELENIUM_DEFAULT_TIMEOUT", "8"))
POLL_INTERVAL = float(os.getenv("SELENIUM_POLL_INTERVAL", "0.5"))
PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", "45"))
IMPLICIT_WAIT = float(os.getenv("SELENIUM_IMPLICIT_WAIT", "0.2"))
WINDOW_SIZE = os.getenv("BROWSER_WINDOW_SIZE", "1440,900")

