import logging

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from ..utils.logging import LOGGER_NAME
from .base import BasePage

logger = logging.getLogger(f"{LOGGER_NAME}.login")


class LoginPage(BasePage):
    def login(self, username: str, password: str) -> None:
        logger.info("Attempting login for %s", username)
        self.open("login")
        self.fill_input('input[name="username"]', username)
        self.fill_input('input[name="password"]', password)
        self.click_by_text("Sign in", "button")
        self.wait_for_text("Lorem ipsum sic dolor amet...")
        logger.info("Login successful for %s", username)

    def logout(self) -> None:
        logger.info("Performing logout")
        self.open("tasks")
        profile_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Profile"]')),
        )
        profile_button.click()

        logout_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, '//li[@role="menuitem" and .="Logout"]')),
        )
        logout_button.click()
        self.wait_for_text("Sign in", "button")
        logger.info("Logout completed")

    def is_logged_in(self) -> bool:
        try:
            self.wait_for_text("Lorem ipsum sic dolor amet...")
        except TimeoutException:
            return False
        return True

    def is_logged_out(self) -> bool:
        try:
            self.wait_for_text("Sign in", "button")
        except TimeoutException:
            return False
        return True

